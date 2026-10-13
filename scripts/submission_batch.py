"""Bounded, data-only discovery of inline and GitHub attachment witnesses.

ZIP members are read directly, never extracted. A top-level MANIFEST.json selects
active native witnesses; source copies, scripts and archived certificates are not
trusted or run. Without a manifest only records/ and witnesses/ JSON are read.
"""
import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import stat
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
import zipfile

MAX_RECORDS = 2000
MAX_ARCHIVES = 8
MAX_DOWNLOAD = 64 * 1024 * 1024
MAX_EXPANDED = 256 * 1024 * 1024
MAX_MEMBER = 8 * 1024 * 1024
MAX_MEMBERS = 12000
ATTACHMENT = re.compile(r'https://github\.com/user-attachments/files/[0-9]+/[^\s<>\]()`]+\.zip(?:\?[^\s<>\]()`]*)?', re.I)


class BatchError(ValueError):
    pass


def safe_path(name):
    path = PurePosixPath(name)
    if (not name or '\\' in name or '\x00' in name or ':' in name or path.is_absolute()
            or any(part in ('..', '.') for part in name.split('/'))):
        raise BatchError('Unsafe archive member path.')
    return path


def allowed_download(url):
    p = urlsplit(url)
    return (p.scheme == 'https' and p.username is None and p.password is None
            and p.port in (None, 443)
            and (p.hostname == 'github.com' and p.path.startswith('/user-attachments/files/')
                 or p.hostname in ('objects.githubusercontent.com', 'github-production-user-asset-6210df.s3.amazonaws.com')
                 or p.hostname == 'release-assets.githubusercontent.com'))


class RestrictedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_download(newurl):
            raise BatchError('Attachment redirected outside the allowed GitHub asset hosts.')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_archive(url):
    if not ATTACHMENT.fullmatch(url) or not allowed_download(url):
        raise BatchError('Only explicit GitHub user-attachment ZIP links are accepted.')
    request = Request(url, headers={'User-Agent': 'platonic-packing-submission-checker'})
    with build_opener(RestrictedRedirect()).open(request, timeout=45) as response:
        if not allowed_download(response.url):
            raise BatchError('Unapproved attachment response URL.')
        declared = response.headers.get('Content-Length')
        if declared and int(declared) > MAX_DOWNLOAD:
            raise BatchError('Attachment exceeds the 64 MiB compressed limit.')
        data = response.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise BatchError('Attachment exceeds the 64 MiB compressed limit.')
    return data


def entries(obj):
    """A piece array is one witness; a record array/dictionary is a batch."""
    if isinstance(obj, dict) and isinstance(obj.get('pieces'), list):
        return [obj]
    if isinstance(obj, list):
        if not obj or all(isinstance(row, list) for row in obj):
            return [{'pieces': obj}]
        return obj
    if isinstance(obj, dict):
        for key in ('records', 'packings', 'constructions'):
            if isinstance(obj.get(key), list):
                return obj[key]
        if obj and all(isinstance(value, dict) for value in obj.values()):
            return list(obj.values())
    return [obj]


def archive_records(data, url):
    archive_sha = hashlib.sha256(data).hexdigest()
    output, ignored = [], 0
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_MEMBERS or sum(i.file_size for i in infos) > MAX_EXPANDED:
                raise BatchError('ZIP exceeds the member-count or expanded-size limit.')
            members = {}
            for info in infos:
                safe_path(info.filename.rstrip('/'))
                if stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1:
                    raise BatchError('Encrypted and symbolic-link ZIP members are not accepted.')
                if info.filename in members:
                    raise BatchError('ZIP contains duplicate member names.')
                members[info.filename] = info
            manifests = [name for name in members if PurePosixPath(name).name == 'MANIFEST.json']
            selected = []
            if manifests:
                depth = min(len(PurePosixPath(name).parts) for name in manifests)
                primary = [name for name in manifests if len(PurePosixPath(name).parts) == depth]
                if len(primary) != 1:
                    raise BatchError('ZIP has ambiguous top-level manifests.')
                manifest_name = primary[0]
                if members[manifest_name].file_size > MAX_MEMBER:
                    raise BatchError('Manifest exceeds the JSON size limit.')
                manifest = json.loads(archive.read(manifest_name))
                cases = manifest.get('cases') if isinstance(manifest, dict) else None
                if not isinstance(cases, list) or len(cases) > MAX_RECORDS:
                    raise BatchError('Manifest needs a bounded cases list.')
                if 'count' in manifest and manifest['count'] != len(cases):
                    raise BatchError('Manifest count does not match its cases list.')
                base = PurePosixPath(manifest_name).parent
                for case in cases:
                    if not isinstance(case, dict):
                        output.append({'source': url, 'error': 'Manifest case is not an object.'})
                        continue
                    relative = case.get('witness', case.get('file'))
                    if not isinstance(relative, str):
                        output.append({'source': url, 'error': 'Manifest case has no native witness/file path.'})
                        continue
                    path = safe_path(relative)
                    # A whitelist never follows submitted references into historical source banks.
                    if path.parts[0] not in ('records', 'witnesses') or path.suffix.lower() != '.json':
                        output.append({'source': f'{url}::{relative}', 'error': 'Only records/ or witnesses/ native JSON may be selected.'})
                        continue
                    selected.append(((base / path).as_posix(), case))
            else:
                for name in members:
                    parts = PurePosixPath(name).parts
                    if (len(parts) >= 2 and 'original' not in parts and 'upstream' not in parts
                            and any(part in ('records', 'witnesses') for part in parts[:-1])
                            and name.lower().endswith('.json')):
                        selected.append((name, {}))
            if len(selected) > MAX_RECORDS:
                raise BatchError('Archive contains too many native witnesses.')
            if not selected and not output:
                raise BatchError('No native 3D witnesses found in records/ or witnesses/.')
            ignored = len(members) - len({name for name, _ in selected})
            for name, case in selected:
                source = f'{url}::{name}'
                try:
                    info = members.get(name)
                    if info is None:
                        raise BatchError('Manifest witness is missing from ZIP.')
                    if info.file_size > MAX_MEMBER:
                        raise BatchError('Witness exceeds the JSON size limit.')
                    raw = archive.read(info)
                    digest = hashlib.sha256(raw).hexdigest()
                    expected = case.get('witness_sha256', case.get('sha256'))
                    if expected is not None and expected != digest:
                        raise BatchError('Witness SHA-256 does not match the manifest.')
                    obj = json.loads(raw)
                    if not isinstance(obj, dict) or not isinstance(obj.get('pieces'), list):
                        raise BatchError('Archive member is not a native 3D packing witness.')
                    output.append({'source': source, 'object': obj, 'metadata': case,
                                   'archive': url, 'archive_sha256': archive_sha, 'witness_sha256': digest})
                except (ValueError, KeyError, zipfile.BadZipFile, UnicodeDecodeError) as exc:
                    output.append({'source': source, 'error': str(exc)})
    except (zipfile.BadZipFile, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BatchError(f'Invalid ZIP or manifest: {exc}') from exc
    return output, ignored


def discover(body, fields, downloader=download_archive):
    candidates, attachments, ignored = [], [], 0
    text = fields.get('packing', '')
    fenced = re.findall(r'```(?:json)?\s*\n(.*?)\n```', text, re.S)
    payloads = fenced if fenced else ([text] if text.strip() else [])
    for block in payloads:
        try:
            obj = json.loads(block)
            for index, value in enumerate(entries(obj), 1):
                candidates.append({'source': f'inline:{len(candidates) + 1}', 'object': value})
                if len(candidates) > MAX_RECORDS:
                    raise BatchError(f'Split batches above {MAX_RECORDS} candidates.')
        except (ValueError, UnicodeDecodeError) as exc:
            candidates.append({'source': 'inline', 'error': f'Packing JSON is invalid: {exc}'})
    urls = list(dict.fromkeys(re.findall(r'https?://[^\s<>\]()`]+\.zip(?:\?[^\s<>\]()`]*)?', body or '', re.I)))
    if len(urls) > MAX_ARCHIVES:
        raise BatchError('At most eight GitHub ZIP attachments are supported per submission.')
    for url in urls:
        try:
            rows, skipped = archive_records(downloader(url), url)
            if len(candidates) + len(rows) > MAX_RECORDS:
                raise BatchError(f'This attachment exceeds the {MAX_RECORDS}-candidate submission limit; split the batch.')
            candidates.extend(rows)
            ignored += skipped
            attachments.append({'url': url, 'native_candidates': len(rows), 'ignored_auxiliary_members': skipped})
        except (ValueError, OSError, zipfile.BadZipFile) as exc:
            candidates.append({'source': url, 'error': f'Attachment rejected: {exc}'})
            attachments.append({'url': url, 'error': str(exc)})
    if not candidates:
        raise BatchError('The Packing field is empty and no supported GitHub ZIP attachment was found.')
    if len(candidates) > MAX_RECORDS:
        raise BatchError(f'Submission has {len(candidates)} candidates; split batches above {MAX_RECORDS}.')
    return candidates, attachments, ignored
