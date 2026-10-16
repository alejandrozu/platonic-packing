import PackingCertificates.Algebraic.FragmentND
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace PackingCertificates.Algebraic.RangeAssembly
open PackingCertificates.Algebraic.FragmentND

theorem cover600 (f : Fin 600 → Bool)
    (h0 : rangeCheck 0 32 (by decide) f = true)
    (h1 : rangeCheck 32 32 (by decide) f = true)
    (h2 : rangeCheck 64 32 (by decide) f = true)
    (h3 : rangeCheck 96 32 (by decide) f = true)
    (h4 : rangeCheck 128 32 (by decide) f = true)
    (h5 : rangeCheck 160 32 (by decide) f = true)
    (h6 : rangeCheck 192 32 (by decide) f = true)
    (h7 : rangeCheck 224 32 (by decide) f = true)
    (h8 : rangeCheck 256 32 (by decide) f = true)
    (h9 : rangeCheck 288 32 (by decide) f = true)
    (h10 : rangeCheck 320 32 (by decide) f = true)
    (h11 : rangeCheck 352 32 (by decide) f = true)
    (h12 : rangeCheck 384 32 (by decide) f = true)
    (h13 : rangeCheck 416 32 (by decide) f = true)
    (h14 : rangeCheck 448 32 (by decide) f = true)
    (h15 : rangeCheck 480 32 (by decide) f = true)
    (h16 : rangeCheck 512 32 (by decide) f = true)
    (h17 : rangeCheck 544 32 (by decide) f = true)
    (h18 : rangeCheck 576 24 (by decide) f = true)
    : ∀ i, f i = true := by
  intro i
  by_cases h288 : i.val < 288
  · by_cases h128 : i.val < 128
    · by_cases h64 : i.val < 64
      · by_cases h32 : i.val < 32
        · exact rangeCheck_sound h0 i (by omega) (by omega)
        · exact rangeCheck_sound h1 i (by omega) (by omega)
      · by_cases h96 : i.val < 96
        · exact rangeCheck_sound h2 i (by omega) (by omega)
        · exact rangeCheck_sound h3 i (by omega) (by omega)
    · by_cases h192 : i.val < 192
      · by_cases h160 : i.val < 160
        · exact rangeCheck_sound h4 i (by omega) (by omega)
        · exact rangeCheck_sound h5 i (by omega) (by omega)
      · by_cases h224 : i.val < 224
        · exact rangeCheck_sound h6 i (by omega) (by omega)
        · by_cases h256 : i.val < 256
          · exact rangeCheck_sound h7 i (by omega) (by omega)
          · exact rangeCheck_sound h8 i (by omega) (by omega)
  · by_cases h448 : i.val < 448
    · by_cases h352 : i.val < 352
      · by_cases h320 : i.val < 320
        · exact rangeCheck_sound h9 i (by omega) (by omega)
        · exact rangeCheck_sound h10 i (by omega) (by omega)
      · by_cases h384 : i.val < 384
        · exact rangeCheck_sound h11 i (by omega) (by omega)
        · by_cases h416 : i.val < 416
          · exact rangeCheck_sound h12 i (by omega) (by omega)
          · exact rangeCheck_sound h13 i (by omega) (by omega)
    · by_cases h512 : i.val < 512
      · by_cases h480 : i.val < 480
        · exact rangeCheck_sound h14 i (by omega) (by omega)
        · exact rangeCheck_sound h15 i (by omega) (by omega)
      · by_cases h544 : i.val < 544
        · exact rangeCheck_sound h16 i (by omega) (by omega)
        · by_cases h576 : i.val < 576
          · exact rangeCheck_sound h17 i (by omega) (by omega)
          · exact rangeCheck_sound h18 i (by omega) (by omega)

#print axioms cover600

theorem cover684 (f : Fin 684 → Bool)
    (h0 : rangeCheck 0 8 (by decide) f = true)
    (h1 : rangeCheck 8 8 (by decide) f = true)
    (h2 : rangeCheck 16 8 (by decide) f = true)
    (h3 : rangeCheck 24 8 (by decide) f = true)
    (h4 : rangeCheck 32 8 (by decide) f = true)
    (h5 : rangeCheck 40 8 (by decide) f = true)
    (h6 : rangeCheck 48 8 (by decide) f = true)
    (h7 : rangeCheck 56 8 (by decide) f = true)
    (h8 : rangeCheck 64 8 (by decide) f = true)
    (h9 : rangeCheck 72 8 (by decide) f = true)
    (h10 : rangeCheck 80 8 (by decide) f = true)
    (h11 : rangeCheck 88 8 (by decide) f = true)
    (h12 : rangeCheck 96 8 (by decide) f = true)
    (h13 : rangeCheck 104 8 (by decide) f = true)
    (h14 : rangeCheck 112 8 (by decide) f = true)
    (h15 : rangeCheck 120 8 (by decide) f = true)
    (h16 : rangeCheck 128 8 (by decide) f = true)
    (h17 : rangeCheck 136 8 (by decide) f = true)
    (h18 : rangeCheck 144 8 (by decide) f = true)
    (h19 : rangeCheck 152 8 (by decide) f = true)
    (h20 : rangeCheck 160 8 (by decide) f = true)
    (h21 : rangeCheck 168 8 (by decide) f = true)
    (h22 : rangeCheck 176 8 (by decide) f = true)
    (h23 : rangeCheck 184 8 (by decide) f = true)
    (h24 : rangeCheck 192 8 (by decide) f = true)
    (h25 : rangeCheck 200 8 (by decide) f = true)
    (h26 : rangeCheck 208 8 (by decide) f = true)
    (h27 : rangeCheck 216 8 (by decide) f = true)
    (h28 : rangeCheck 224 8 (by decide) f = true)
    (h29 : rangeCheck 232 8 (by decide) f = true)
    (h30 : rangeCheck 240 8 (by decide) f = true)
    (h31 : rangeCheck 248 8 (by decide) f = true)
    (h32 : rangeCheck 256 8 (by decide) f = true)
    (h33 : rangeCheck 264 8 (by decide) f = true)
    (h34 : rangeCheck 272 8 (by decide) f = true)
    (h35 : rangeCheck 280 8 (by decide) f = true)
    (h36 : rangeCheck 288 8 (by decide) f = true)
    (h37 : rangeCheck 296 8 (by decide) f = true)
    (h38 : rangeCheck 304 8 (by decide) f = true)
    (h39 : rangeCheck 312 8 (by decide) f = true)
    (h40 : rangeCheck 320 8 (by decide) f = true)
    (h41 : rangeCheck 328 8 (by decide) f = true)
    (h42 : rangeCheck 336 8 (by decide) f = true)
    (h43 : rangeCheck 344 8 (by decide) f = true)
    (h44 : rangeCheck 352 8 (by decide) f = true)
    (h45 : rangeCheck 360 8 (by decide) f = true)
    (h46 : rangeCheck 368 8 (by decide) f = true)
    (h47 : rangeCheck 376 8 (by decide) f = true)
    (h48 : rangeCheck 384 8 (by decide) f = true)
    (h49 : rangeCheck 392 8 (by decide) f = true)
    (h50 : rangeCheck 400 8 (by decide) f = true)
    (h51 : rangeCheck 408 8 (by decide) f = true)
    (h52 : rangeCheck 416 8 (by decide) f = true)
    (h53 : rangeCheck 424 8 (by decide) f = true)
    (h54 : rangeCheck 432 8 (by decide) f = true)
    (h55 : rangeCheck 440 8 (by decide) f = true)
    (h56 : rangeCheck 448 8 (by decide) f = true)
    (h57 : rangeCheck 456 8 (by decide) f = true)
    (h58 : rangeCheck 464 8 (by decide) f = true)
    (h59 : rangeCheck 472 8 (by decide) f = true)
    (h60 : rangeCheck 480 8 (by decide) f = true)
    (h61 : rangeCheck 488 8 (by decide) f = true)
    (h62 : rangeCheck 496 8 (by decide) f = true)
    (h63 : rangeCheck 504 8 (by decide) f = true)
    (h64 : rangeCheck 512 8 (by decide) f = true)
    (h65 : rangeCheck 520 8 (by decide) f = true)
    (h66 : rangeCheck 528 8 (by decide) f = true)
    (h67 : rangeCheck 536 8 (by decide) f = true)
    (h68 : rangeCheck 544 8 (by decide) f = true)
    (h69 : rangeCheck 552 8 (by decide) f = true)
    (h70 : rangeCheck 560 8 (by decide) f = true)
    (h71 : rangeCheck 568 8 (by decide) f = true)
    (h72 : rangeCheck 576 8 (by decide) f = true)
    (h73 : rangeCheck 584 8 (by decide) f = true)
    (h74 : rangeCheck 592 8 (by decide) f = true)
    (h75 : rangeCheck 600 8 (by decide) f = true)
    (h76 : rangeCheck 608 8 (by decide) f = true)
    (h77 : rangeCheck 616 8 (by decide) f = true)
    (h78 : rangeCheck 624 8 (by decide) f = true)
    (h79 : rangeCheck 632 8 (by decide) f = true)
    (h80 : rangeCheck 640 8 (by decide) f = true)
    (h81 : rangeCheck 648 8 (by decide) f = true)
    (h82 : rangeCheck 656 8 (by decide) f = true)
    (h83 : rangeCheck 664 8 (by decide) f = true)
    (h84 : rangeCheck 672 8 (by decide) f = true)
    (h85 : rangeCheck 680 4 (by decide) f = true)
    : ∀ i, f i = true := by
  intro i
  by_cases h344 : i.val < 344
  · by_cases h168 : i.val < 168
    · by_cases h80 : i.val < 80
      · by_cases h40 : i.val < 40
        · by_cases h16 : i.val < 16
          · by_cases h8 : i.val < 8
            · exact rangeCheck_sound h0 i (by omega) (by omega)
            · exact rangeCheck_sound h1 i (by omega) (by omega)
          · by_cases h24 : i.val < 24
            · exact rangeCheck_sound h2 i (by omega) (by omega)
            · by_cases h32 : i.val < 32
              · exact rangeCheck_sound h3 i (by omega) (by omega)
              · exact rangeCheck_sound h4 i (by omega) (by omega)
        · by_cases h56 : i.val < 56
          · by_cases h48 : i.val < 48
            · exact rangeCheck_sound h5 i (by omega) (by omega)
            · exact rangeCheck_sound h6 i (by omega) (by omega)
          · by_cases h64 : i.val < 64
            · exact rangeCheck_sound h7 i (by omega) (by omega)
            · by_cases h72 : i.val < 72
              · exact rangeCheck_sound h8 i (by omega) (by omega)
              · exact rangeCheck_sound h9 i (by omega) (by omega)
      · by_cases h120 : i.val < 120
        · by_cases h96 : i.val < 96
          · by_cases h88 : i.val < 88
            · exact rangeCheck_sound h10 i (by omega) (by omega)
            · exact rangeCheck_sound h11 i (by omega) (by omega)
          · by_cases h104 : i.val < 104
            · exact rangeCheck_sound h12 i (by omega) (by omega)
            · by_cases h112 : i.val < 112
              · exact rangeCheck_sound h13 i (by omega) (by omega)
              · exact rangeCheck_sound h14 i (by omega) (by omega)
        · by_cases h144 : i.val < 144
          · by_cases h128 : i.val < 128
            · exact rangeCheck_sound h15 i (by omega) (by omega)
            · by_cases h136 : i.val < 136
              · exact rangeCheck_sound h16 i (by omega) (by omega)
              · exact rangeCheck_sound h17 i (by omega) (by omega)
          · by_cases h152 : i.val < 152
            · exact rangeCheck_sound h18 i (by omega) (by omega)
            · by_cases h160 : i.val < 160
              · exact rangeCheck_sound h19 i (by omega) (by omega)
              · exact rangeCheck_sound h20 i (by omega) (by omega)
    · by_cases h256 : i.val < 256
      · by_cases h208 : i.val < 208
        · by_cases h184 : i.val < 184
          · by_cases h176 : i.val < 176
            · exact rangeCheck_sound h21 i (by omega) (by omega)
            · exact rangeCheck_sound h22 i (by omega) (by omega)
          · by_cases h192 : i.val < 192
            · exact rangeCheck_sound h23 i (by omega) (by omega)
            · by_cases h200 : i.val < 200
              · exact rangeCheck_sound h24 i (by omega) (by omega)
              · exact rangeCheck_sound h25 i (by omega) (by omega)
        · by_cases h232 : i.val < 232
          · by_cases h216 : i.val < 216
            · exact rangeCheck_sound h26 i (by omega) (by omega)
            · by_cases h224 : i.val < 224
              · exact rangeCheck_sound h27 i (by omega) (by omega)
              · exact rangeCheck_sound h28 i (by omega) (by omega)
          · by_cases h240 : i.val < 240
            · exact rangeCheck_sound h29 i (by omega) (by omega)
            · by_cases h248 : i.val < 248
              · exact rangeCheck_sound h30 i (by omega) (by omega)
              · exact rangeCheck_sound h31 i (by omega) (by omega)
      · by_cases h296 : i.val < 296
        · by_cases h272 : i.val < 272
          · by_cases h264 : i.val < 264
            · exact rangeCheck_sound h32 i (by omega) (by omega)
            · exact rangeCheck_sound h33 i (by omega) (by omega)
          · by_cases h280 : i.val < 280
            · exact rangeCheck_sound h34 i (by omega) (by omega)
            · by_cases h288 : i.val < 288
              · exact rangeCheck_sound h35 i (by omega) (by omega)
              · exact rangeCheck_sound h36 i (by omega) (by omega)
        · by_cases h320 : i.val < 320
          · by_cases h304 : i.val < 304
            · exact rangeCheck_sound h37 i (by omega) (by omega)
            · by_cases h312 : i.val < 312
              · exact rangeCheck_sound h38 i (by omega) (by omega)
              · exact rangeCheck_sound h39 i (by omega) (by omega)
          · by_cases h328 : i.val < 328
            · exact rangeCheck_sound h40 i (by omega) (by omega)
            · by_cases h336 : i.val < 336
              · exact rangeCheck_sound h41 i (by omega) (by omega)
              · exact rangeCheck_sound h42 i (by omega) (by omega)
  · by_cases h512 : i.val < 512
    · by_cases h424 : i.val < 424
      · by_cases h384 : i.val < 384
        · by_cases h360 : i.val < 360
          · by_cases h352 : i.val < 352
            · exact rangeCheck_sound h43 i (by omega) (by omega)
            · exact rangeCheck_sound h44 i (by omega) (by omega)
          · by_cases h368 : i.val < 368
            · exact rangeCheck_sound h45 i (by omega) (by omega)
            · by_cases h376 : i.val < 376
              · exact rangeCheck_sound h46 i (by omega) (by omega)
              · exact rangeCheck_sound h47 i (by omega) (by omega)
        · by_cases h400 : i.val < 400
          · by_cases h392 : i.val < 392
            · exact rangeCheck_sound h48 i (by omega) (by omega)
            · exact rangeCheck_sound h49 i (by omega) (by omega)
          · by_cases h408 : i.val < 408
            · exact rangeCheck_sound h50 i (by omega) (by omega)
            · by_cases h416 : i.val < 416
              · exact rangeCheck_sound h51 i (by omega) (by omega)
              · exact rangeCheck_sound h52 i (by omega) (by omega)
      · by_cases h464 : i.val < 464
        · by_cases h440 : i.val < 440
          · by_cases h432 : i.val < 432
            · exact rangeCheck_sound h53 i (by omega) (by omega)
            · exact rangeCheck_sound h54 i (by omega) (by omega)
          · by_cases h448 : i.val < 448
            · exact rangeCheck_sound h55 i (by omega) (by omega)
            · by_cases h456 : i.val < 456
              · exact rangeCheck_sound h56 i (by omega) (by omega)
              · exact rangeCheck_sound h57 i (by omega) (by omega)
        · by_cases h488 : i.val < 488
          · by_cases h472 : i.val < 472
            · exact rangeCheck_sound h58 i (by omega) (by omega)
            · by_cases h480 : i.val < 480
              · exact rangeCheck_sound h59 i (by omega) (by omega)
              · exact rangeCheck_sound h60 i (by omega) (by omega)
          · by_cases h496 : i.val < 496
            · exact rangeCheck_sound h61 i (by omega) (by omega)
            · by_cases h504 : i.val < 504
              · exact rangeCheck_sound h62 i (by omega) (by omega)
              · exact rangeCheck_sound h63 i (by omega) (by omega)
    · by_cases h600 : i.val < 600
      · by_cases h552 : i.val < 552
        · by_cases h528 : i.val < 528
          · by_cases h520 : i.val < 520
            · exact rangeCheck_sound h64 i (by omega) (by omega)
            · exact rangeCheck_sound h65 i (by omega) (by omega)
          · by_cases h536 : i.val < 536
            · exact rangeCheck_sound h66 i (by omega) (by omega)
            · by_cases h544 : i.val < 544
              · exact rangeCheck_sound h67 i (by omega) (by omega)
              · exact rangeCheck_sound h68 i (by omega) (by omega)
        · by_cases h576 : i.val < 576
          · by_cases h560 : i.val < 560
            · exact rangeCheck_sound h69 i (by omega) (by omega)
            · by_cases h568 : i.val < 568
              · exact rangeCheck_sound h70 i (by omega) (by omega)
              · exact rangeCheck_sound h71 i (by omega) (by omega)
          · by_cases h584 : i.val < 584
            · exact rangeCheck_sound h72 i (by omega) (by omega)
            · by_cases h592 : i.val < 592
              · exact rangeCheck_sound h73 i (by omega) (by omega)
              · exact rangeCheck_sound h74 i (by omega) (by omega)
      · by_cases h640 : i.val < 640
        · by_cases h616 : i.val < 616
          · by_cases h608 : i.val < 608
            · exact rangeCheck_sound h75 i (by omega) (by omega)
            · exact rangeCheck_sound h76 i (by omega) (by omega)
          · by_cases h624 : i.val < 624
            · exact rangeCheck_sound h77 i (by omega) (by omega)
            · by_cases h632 : i.val < 632
              · exact rangeCheck_sound h78 i (by omega) (by omega)
              · exact rangeCheck_sound h79 i (by omega) (by omega)
        · by_cases h664 : i.val < 664
          · by_cases h648 : i.val < 648
            · exact rangeCheck_sound h80 i (by omega) (by omega)
            · by_cases h656 : i.val < 656
              · exact rangeCheck_sound h81 i (by omega) (by omega)
              · exact rangeCheck_sound h82 i (by omega) (by omega)
          · by_cases h672 : i.val < 672
            · exact rangeCheck_sound h83 i (by omega) (by omega)
            · by_cases h680 : i.val < 680
              · exact rangeCheck_sound h84 i (by omega) (by omega)
              · exact rangeCheck_sound h85 i (by omega) (by omega)

#print axioms cover684

end PackingCertificates.Algebraic.RangeAssembly

