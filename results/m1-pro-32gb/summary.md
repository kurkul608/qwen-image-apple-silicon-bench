## Time, memory and stability

| Model | Size | Finished | Mean time | Range | Per step | Peak memory | Peak swap | Thermal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Turbo Q4_K_M | 1024x1024 | 8/8 | 5:10 | 5:08-5:12 | 33 s | 16.2 GB | 2.0 GB | 0 |
| Turbo Q4_K_M | 1024x1536 | 2/2 | 10:58 | 10:56-10:59 | 54 s | 17.8 GB | 2.6 GB | 0 |
| Turbo Q8_0 | 1024x1024 | 8/8 | 5:01 | 4:58-5:03 | 31 s | 23.3 GB | 2.0 GB | 0 |
| Turbo Q8_0 | 1024x1536 | 2/2 | 10:38 | 10:37-10:39 | 51 s | 24.9 GB | 5.4 GB | 0 |
| Base Q8_0 | 1024x1024 | 4/4 | 21:37 | 21:35-21:39 | 31 s | 23.4 GB | 2.0 GB | 0 |
| Base Q8_0 | 1024x1536 | 1/1 | 37:49 | 37:49-37:49 | 51 s | 24.9 GB | 6.5 GB | 0 |
| Original F16 | 1024x1024 | 4/4 | 23:18 | 23:01-23:31 | 30 s | 44.1 GB | 21.2 GB | 0 |
| Original F16 | 1024x1536 | 1/1 | 59:16 | 59:16-59:16 | 49 s | 45.7 GB | 22.6 GB | 0 |
| Base Q8_0, CFG 6 | 1024x1024 | 4/4 | 21:40 | 21:36-21:44 | 62 s | 23.4 GB | 3.6 GB | 0 |
| Base Q8_0, CFG 6 | 1024x1536 | 1/1 | 37:12 | 37:12-37:12 | 100 s | 25.0 GB | 6.6 GB | 0 |
| Original F16, CFG 6 | 1024x1024 | 1/1 | 23:48 | 23:48-23:48 | 60 s | 44.1 GB | 21.1 GB | 0 |

## Time per stage

| Model | Size | Text encoder | Sampling | VAE decode |
| --- | --- | --- | --- | --- |
| Turbo Q4_K_M | 1024x1024 | 14 s | 270 s | 26 s |
| Turbo Q4_K_M | 1024x1536 | 163 s | 454 s | 41 s |
| Turbo Q8_0 | 1024x1024 | 15 s | 260 s | 27 s |
| Turbo Q8_0 | 1024x1536 | 163 s | 436 s | 40 s |
| Base Q8_0 | 1024x1024 | 14 s | 1256 s | 27 s |
| Base Q8_0 | 1024x1536 | 163 s | 2068 s | 39 s |
| Original F16 | 1024x1024 | 94 s | 1278 s | 26 s |
| Original F16 | 1024x1536 | 1450 s | 2067 s | 39 s |

## Pixel comparison

| Pair | Prompt | SSIM | PSNR |
| --- | --- | --- | --- |
| Quantization: Turbo Q4 vs Q8 | 1-portrait | 0.9148 | 25.9 dB |
| Quantization: Turbo Q4 vs Q8 | 2-motion | 0.8824 | 23.0 dB |
| Quantization: Turbo Q4 vs Q8 | 3-typography | 0.8987 | 16.1 dB |
| Quantization: Turbo Q4 vs Q8 | 4-ui | 0.9353 | 17.6 dB |
| Quantization: Turbo Q4 vs Q8 | 5-official-poster | 0.5975 | 11.4 dB |
| Quantization: Base Q8 vs Original F16 | 1-portrait | 0.9964 | 44.7 dB |
| Quantization: Base Q8 vs Original F16 | 2-motion | 0.9894 | 32.3 dB |
| Quantization: Base Q8 vs Original F16 | 3-typography | 0.9686 | 22.8 dB |
| Quantization: Base Q8 vs Original F16 | 4-ui | 0.9577 | 20.2 dB |
| Quantization: Base Q8 vs Original F16 | 5-official-poster | 0.8718 | 17.6 dB |
| Repeatability: Turbo Q8 run 1 vs 2 | 1-portrait | 1.0000 | identical |
| Repeatability: Turbo Q8 run 1 vs 2 | 2-motion | 1.0000 | identical |
| Repeatability: Turbo Q8 run 1 vs 2 | 3-typography | 1.0000 | identical |
| Repeatability: Turbo Q8 run 1 vs 2 | 4-ui | 1.0000 | identical |
| Repeatability: Turbo Q8 run 1 vs 2 | 5-official-poster | 1.0000 | identical |
| Repeatability: Turbo Q4 run 1 vs 2 | 1-portrait | 1.0000 | identical |
| Repeatability: Turbo Q4 run 1 vs 2 | 2-motion | 1.0000 | identical |
| Repeatability: Turbo Q4 run 1 vs 2 | 3-typography | 1.0000 | identical |
| Repeatability: Turbo Q4 run 1 vs 2 | 4-ui | 1.0000 | identical |
| Repeatability: Turbo Q4 run 1 vs 2 | 5-official-poster | 1.0000 | identical |

## Quality review

| Model | Prompt | Text accuracy | Anatomy | Prompt match | Artifacts | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Turbo Q4_K_M | 1-portrait | n/a | ok | yes | none | Fewer loose threads than asked. |
| Turbo Q8_0 | 1-portrait | n/a | ok | yes | none | Same composition as Q4, slightly more texture. |
| Base Q8_0 | 1-portrait | n/a | ok | yes | none | Most skin and wool detail; loose threads visible. |
| Original F16 | 1-portrait | n/a | ok | yes | none | Hard to tell apart from Base Q8. |
| Turbo Q4_K_M | 2-motion | n/a | ok | yes | none | Both legs extended, five fingers per hand. |
| Turbo Q8_0 | 2-motion | n/a | ok | yes | none | Almost the same image as Q4. |
| Base Q8_0 | 2-motion | n/a | ok | yes | none | Profile view, visible stage curtain. |
| Original F16 | 2-motion | n/a | ok | yes | none | Hard to tell apart from Base Q8. |
| Turbo Q4_K_M | 3-typography | all correct | n/a | yes | none | Circle overlaps the title as asked. |
| Turbo Q8_0 | 3-typography | all correct | n/a | yes | none | Circle overlaps the title as asked. |
| Base Q8_0 | 3-typography | all correct | n/a | partial | none | Circle sits next to the title, does not overlap it. |
| Original F16 | 3-typography | all correct | n/a | partial | none | Same layout as Base Q8, circle does not overlap. |
| Turbo Q4_K_M | 4-ui | all correct | n/a | yes | none | Four labeled bars, but the bars carry no values. |
| Turbo Q8_0 | 4-ui | all correct | n/a | yes | none | Same as Q4. |
| Base Q8_0 | 4-ui | all correct | n/a | partial | none | Two progress bars instead of a four-bar chart; labels float. |
| Original F16 | 4-ui | all correct | n/a | partial | none | Same layout as Base Q8. |
| Turbo Q4_K_M | 5-official-poster | many errors | n/a | yes | garbled small text | Reactivity series skips Fe and repeats Pt; table has a wrong extra Copper column. |
| Turbo Q8_0 | 5-official-poster | few errors | n/a | yes | garbled small text | Series and table correct; two table cells and one side note garbled. |
| Base Q8_0 | 5-official-poster | 1 error | n/a | yes | none | Hg repeated in the series; table and notes clean. |
| Original F16 | 5-official-poster | all correct | n/a | yes | none | Cleanest poster: series, table and notes correct. |
