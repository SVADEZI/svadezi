# Swadezi Gold — Product Image Naming Guide

## SKU Format

```
[CATEGORY CODE]-[NUMBER]
```

| Category        | Code | Example SKU |
|-----------------|------|-------------|
| Mangal Sutra    | MS   | MS-001      |
| Ring (Gold)     | RG   | RG-001      |
| Ring (Diamond)  | RD   | RD-001      |
| Necklace (Gold) | NG   | NG-001      |
| Necklace (Diam) | ND   | ND-001      |
| Earring (Gold)  | EG   | EG-001      |
| Earring (Diam)  | ED   | ED-001      |
| Bangle (Gold)   | BG   | BG-001      |
| Bangle (Diam)   | BD   | BD-001      |
| Pendant (Gold)  | PG   | PG-001      |
| Pendant (Diam)  | PD   | PD-001      |
| Chain           | CG   | CG-001      |
| Bracelet (Gold) | BR   | BR-001      |
| Anklet          | AN   | AN-001      |
| Nose Ring       | NR   | NR-001      |
| Maang Tikka     | MT   | MT-001      |
| Haar            | HR   | HR-001      |

## Image File Naming

```
[SKU]-[view].jpg
```

| View      | Suffix   | Example           |
|-----------|----------|-------------------|
| Front     | -front   | RG-001-front.jpg  |
| Side      | -side    | RG-001-side.jpg   |
| Top       | -top     | RG-001-top.jpg    |
| Close-up  | -close   | RG-001-close.jpg  |
| On model  | -model   | RG-001-model.jpg  |

## Folder Structure

```
products/
  images/
    mangal-sutra/
    rings/
      gold-rings/
      diamond-rings/
    necklaces/
      gold-necklaces/
      diamond-necklaces/
      sets/
    earrings/
      studs/
      drops/
      jhumkas/
      chandbali/
      hoops/
      tops/
    bangles/
      gold-bangles/
      diamond-bangles/
    pendants/
      gold-pendants/
      diamond-pendants/
    chains/
      gold-chains/
    bracelets/
      gold-bracelets/
      diamond-bracelets/
    anklets/
      gold-anklets/
    nose-rings/
      gold-nose-rings/
    maang-tikka/
    haar/
  data/
    products.json         ← product data with all measurements
    products-template.csv ← fill this in from manufacturer sheets
```

## Measurement Fields (from Manufacturer)

| Field            | Notes                              |
|------------------|------------------------------------|
| weight_grams     | Net gold weight                    |
| purity_karat     | 18K / 22K / 24K                   |
| length_cm        | For necklaces, chains, bangles     |
| ring_size        | Indian size (e.g. 10, 12, 14, 16) |
| diamond_carat    | Total diamond weight               |
| diamond_clarity  | IF / VVS1 / VVS2 / VS1 / VS2 / SI1|
| diamond_color    | D / E / F / G / H                  |
| diamond_pieces   | Number of diamonds set             |
