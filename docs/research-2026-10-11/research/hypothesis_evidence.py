"""Reproduce shell, contact and pose-deletion evidence for Paper 2 hypotheses.

Uses the frozen JSON archive and previously generated double-precision geometry
tables. This is structural evidence, not an optimality or exact-contact proof.
Run: python hypothesis_evidence.py --repo PATH --analysis PATH --out PATH
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def norm(v):
    return math.sqrt(sum(x*x for x in v))


def distance(a, b):
    return norm([x-y for x, y in zip(a, b)])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--analysis', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    geom = json.loads((args.analysis/'geometry-details.json').read_text())
    solid = json.loads((args.repo/'src/solids.json').read_text())
    metrics = {r['record_id']:r for r in csv.DictReader((args.analysis/'record-metrics.csv').open())}
    pair_rows = [r for r in csv.DictReader((args.analysis/'pair-metrics.csv').open()) if r['record_id']=='dodindod_n33']
    poses = json.loads((args.repo/'records/dodindod/dodindod_n33.json').read_text())['pieces']
    radii = [norm(q[:3]) for q in poses]
    central = [i for i,r in enumerate(radii) if r < 1e-8]
    inner = [i for i,r in enumerate(radii) if 1e-8 <= r < 3]
    outer = [i for i,r in enumerate(radii) if r >= 3]
    classes = {i:name for name,indices in [('central',central),('inner',inner),('outer',outer)] for i in indices}
    detail = geom['dodindod_n33']
    counts = {}
    for i,j in detail['contacts']['0.0001']['edges']:
        label = '-'.join(sorted([classes[i],classes[j]]))
        counts[label] = counts.get(label,0)+1
    # Canonical coordinate convention is shared by piece and container files.
    fits = {}
    for name,indices in [('icosahedron',inner),('dodecahedron',outer)]:
        # The inner shell uses the dual orientation of the dodecahedron's
        # normals, not the independently oriented canonical ico vertex file.
        vectors = solid['dodecahedron']['normals'] if name=='icosahedron' else solid[name]['V']
        targets = [[x/norm(v) for x in v] for v in vectors]
        errors = [min(distance([x/radii[i] for x in poses[i][:3]],v) for v in targets) for i in indices]
        fits[name] = {'shell_count':len(indices), 'canonical_vertex_count':len(targets),
                      'max_unit_direction_residual':max(errors),
                      'radius_min':min(radii[i] for i in indices), 'radius_max':max(radii[i] for i in indices)}
    inner_pairs = []
    for component in detail['orientation_components']['1.0']:
        if len(component)==2:
            i,j=component
            inner_pairs.append({'indices':component,'antipodal_centre_residual':norm([poses[i][k]+poses[j][k] for k in range(3)])})
    # Float equality and Euclidean differences are recorded separately.
    deletion = []
    for n in range(29,33):
        smaller=json.loads((args.repo/f'records/dodindod/dodindod_n{n:02d}.json').read_text())['pieces']
        used = set()
        matched=[]
        residuals=[]
        pose_errors=[]
        for q in smaller:
            i=min((i for i in range(33) if i not in used),key=lambda i:distance(q[:3],poses[i][:3]))
            used.add(i); matched.append(i)
            residuals.append(distance(q[:3],poses[i][:3]))
            pose_errors.append(max(abs(a-b) for a,b in zip(q,poses[i])))
        deletion.append({'n':n,'matched_n33_indices':matched,'omitted_n33_indices':sorted(set(range(33))-used),
                         'max_centre_distance':max(residuals),'max_pose_coordinate_difference':max(pose_errors),
                         'all_poses_bitwise_equal':all(small==poses[i] for small,i in zip(smaller,matched)),
                         'omitted_classes':[classes[i] for i in sorted(set(range(33))-used)]})
    contact_rows=[r for r in pair_rows if r['euclidean_distance_if_near'] and float(r['euclidean_distance_if_near'])<=1e-4]
    aligned_rows=[r for r in pair_rows if float(r['misorientation_deg'])<=1]
    # These same-orientation pairs are outside the near-pair computation when
    # bounding radii reject them; no uncomputed distance is invented.
    contact_angles=[float(r['misorientation_deg']) for r in contact_rows]
    class_angles={}
    for r in contact_rows:
        i,j=int(r['i']),int(r['j'])
        label='-'.join(sorted([classes[i],classes[j]]))
        class_angles.setdefault(label,[]).append(float(r['misorientation_deg']))
    nearest={}
    for name,pairs in [('inner-inner',[(i,j) for i in inner for j in inner if i<j]),
                       ('inner-outer',[(i,j) for i in inner for j in outer])]:
        dd=[(i,j,distance(poses[i][:3],poses[j][:3])) for i,j in pairs]
        smallest=min(d for i,j,d in dd)
        close={tuple(sorted((i,j))) for i,j,d in dd if abs(d-smallest)<=1e-9}
        actual={tuple(sorted((i,j))) for i,j in detail['contacts']['0.0001']['edges']
                if '-'.join(sorted([classes[i],classes[j]]))==name}
        nearest[name]={'nearest_centre_distance':smallest,'nearest_pair_count':len(close),
                       'contacts_equal_nearest_shell_pairs':close==actual}
    subset_metrics=[]
    for n in range(29,35):
        r=metrics[f'dodindod_n{n:02d}']
        subset_metrics.append({k:r[k] for k in ['record_id','s_full','density','orientation_components_0.1deg','orientation_components_1.0deg','orientation_components_5.0deg','orientation_largest_fraction_1.0deg','grains_1.0deg','contact_edges_1e-05','contact_edges_0.0001','contact_edges_0.001','wall_near_pieces_0.0001']})
    ico_poses=json.loads((args.repo/'records/icoindod/icoindod_n15.json').read_text())['pieces']
    ico_detail=geom['icoindod_n15']
    ico_outlier=[c[0] for c in ico_detail['orientation_components']['1.0'] if len(c)==1]
    assert ico_outlier==[11]
    outlier_pose=ico_poses[ico_outlier[0]]
    ico_evidence={'record_id':'icoindod_n15','orientation_component_sizes':[len(c) for c in ico_detail['orientation_components']['1.0']],
                  'singleton_piece_index':ico_outlier[0],'singleton_centre_radius':norm(outlier_pose[:3]),
                  'singleton_contact_degree':ico_detail['contacts']['0.0001']['degrees'][ico_outlier[0]],
                  'wall_near_count':int(float(metrics['icoindod_n15']['wall_near_pieces_0.0001']))}
    result={'description':'Double-precision structural evidence; exact archive feasibility is established separately.',
            'input_sha256':{path.relative_to(args.repo).as_posix():hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in [args.repo/'src/solids.json',args.repo/'records/icoindod/icoindod_n15.json',
                                         *(args.repo/f'records/dodindod/dodindod_n{n:02d}.json' for n in range(29,34))]},
            'central_indices':central,'inner_indices':inner,'outer_indices':outer,'canonical_shell_fits':fits,
            'orientation_component_sizes_1deg':[len(c) for c in detail['orientation_components']['1.0']],
            'inner_same_orientation_antipodal_pairs':inner_pairs,'contact_class_counts_1e4':counts,
            'contact_degree_by_class':{name:[detail['contacts']['0.0001']['degrees'][i] for i in indices]
                                       for name,indices in [('central',central),('inner',inner),('outer',outer)]},
            'contact_angle_min_deg':min(contact_angles),'contact_angle_max_deg':max(contact_angles),
            'contact_disorientation_by_class':{name:{'min_deg':min(aa),'max_deg':max(aa)} for name,aa in class_angles.items()},
            'nearest_shell_contact_comparisons':nearest,
            'icoindod_15_central_orientation_exception':ico_evidence,
            'same_orientation_pair_count_1deg':len(aligned_rows),'deletion_comparisons':deletion,'metrics':subset_metrics}
    assert len(central)==1 and len(inner)==12 and len(outer)==20
    assert counts=={'inner-outer':60,'inner-inner':30,'central-inner':12}
    assert min(contact_angles)>5
    assert all(f['max_unit_direction_residual']<1e-12 for f in fits.values())
    assert all(v['contacts_equal_nearest_shell_pairs'] for v in nearest.values())
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['canonical_shell_fits','contact_class_counts_1e4','contact_angle_min_deg','contact_angle_max_deg','deletion_comparisons']},indent=2))


if __name__=='__main__':
    main()
