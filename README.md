# Translator
Translate from one language to another.

```zsh
❯ translate --source eng_Latn --target fra_Latn "This is an original sentence."
C'est une phrase originale.

❯ translate --help
usage: translate [-h] [-v] [-s SOURCE] [-t TARGET] [-l MAX_LENGTH] [-m MODEL_ID]
               [-p PIPELINE] [-L]
               [sentence ...]

Translate from one language to another.

positional arguments:
  sentence              Something to translate.

options:
  -h, --help            show this help message and exit
  -v, --version         shows the current version of translator
  -s SOURCE, --source SOURCE
                        Source language to translate.
  -t TARGET, --target TARGET
                        Target language to translate.
  -l MAX_LENGTH, --max_length MAX_LENGTH
                        Max length of output.
  -m MODEL_ID, --model_id MODEL_ID
                        HuggingFace model ID to use.
  -p PIPELINE, --pipeline PIPELINE
                        Pipeline task to use.
  -L, --language_list   Show list of languages.


❯ translate --language_list
Language list:
- ace_Arab
- ace_Latn
- acm_Arab
- acq_Arab
- aeb_Arab
- afr_Latn
- ajp_Arab
- aka_Latn
- amh_Ethi
- apc_Arab
- arb_Arab
- ars_Arab
- ary_Arab
- arz_Arab
- asm_Beng
- ast_Latn
- awa_Deva
- ayr_Latn
- azb_Arab
- azj_Latn
- bak_Cyrl
- bam_Latn
- ban_Latn
- bel_Cyrl
- bem_Latn
- ben_Beng
- bho_Deva
- bjn_Arab
- bjn_Latn
- bod_Tibt
- bos_Latn
- bug_Latn
- bul_Cyrl
- cat_Latn
- ceb_Latn
- ces_Latn
- cjk_Latn
- ckb_Arab
- crh_Latn
- cym_Latn
- dan_Latn
- deu_Latn
- dik_Latn
- dyu_Latn
- dzo_Tibt
- ell_Grek
- eng_Latn
- epo_Latn
- est_Latn
- eus_Latn
- ewe_Latn
- fao_Latn
- pes_Arab
- fij_Latn
- fin_Latn
- fon_Latn
- fra_Latn
- fur_Latn
- fuv_Latn
- gla_Latn
- gle_Latn
- glg_Latn
- grn_Latn
- guj_Gujr
- hat_Latn
- hau_Latn
- heb_Hebr
- hin_Deva
- hne_Deva
- hrv_Latn
- hun_Latn
- hye_Armn
- ibo_Latn
- ilo_Latn
- ind_Latn
- isl_Latn
- ita_Latn
- jav_Latn
- jpn_Jpan
- kab_Latn
- kac_Latn
- kam_Latn
- kan_Knda
- kas_Arab
- kas_Deva
- kat_Geor
- knc_Arab
- knc_Latn
- kaz_Cyrl
- kbp_Latn
- kea_Latn
- khm_Khmr
- kik_Latn
- kin_Latn
- kir_Cyrl
- kmb_Latn
- kon_Latn
- kor_Hang
- kmr_Latn
- lao_Laoo
- lvs_Latn
- lij_Latn
- lim_Latn
- lin_Latn
- lit_Latn
- lmo_Latn
- ltg_Latn
- ltz_Latn
- lua_Latn
- lug_Latn
- luo_Latn
- lus_Latn
- mag_Deva
- mai_Deva
- mal_Mlym
- mar_Deva
- min_Latn
- mkd_Cyrl
- plt_Latn
- mlt_Latn
- mni_Beng
- khk_Cyrl
- mos_Latn
- mri_Latn
- zsm_Latn
- mya_Mymr
- nld_Latn
- nno_Latn
- nob_Latn
- npi_Deva
- nso_Latn
- nus_Latn
- nya_Latn
- oci_Latn
- gaz_Latn
- ory_Orya
- pag_Latn
- pan_Guru
- pap_Latn
- pol_Latn
- por_Latn
- prs_Arab
- pbt_Arab
- quy_Latn
- ron_Latn
- run_Latn
- rus_Cyrl
- sag_Latn
- san_Deva
- sat_Beng
- scn_Latn
- shn_Mymr
- sin_Sinh
- slk_Latn
- slv_Latn
- smo_Latn
- sna_Latn
- snd_Arab
- som_Latn
- sot_Latn
- spa_Latn
- als_Latn
- srd_Latn
- srp_Cyrl
- ssw_Latn
- sun_Latn
- swe_Latn
- swh_Latn
- szl_Latn
- tam_Taml
- tat_Cyrl
- tel_Telu
- tgk_Cyrl
- tgl_Latn
- tha_Thai
- tir_Ethi
- taq_Latn
- taq_Tfng
- tpi_Latn
- tsn_Latn
- tso_Latn
- tuk_Latn
- tum_Latn
- tur_Latn
- twi_Latn
- tzm_Tfng
- uig_Arab
- ukr_Cyrl
- umb_Latn
- urd_Arab
- uzn_Latn
- vec_Latn
- vie_Latn
- war_Latn
- wol_Latn
- xho_Latn
- ydd_Hebr
- yor_Latn
- yue_Hant
- zho_Hans
- zho_Hant
- zul_Latn

```

Uses Meta's NLLB model [`facebook/nllb-200-distilled-600M`](https://huggingface.co/facebook/nllb-200-distilled-600M) by default. You can change it by passing a custom flag `--model_id`.

# License

This project is distributed under [Mozilla Public License 2.0](LICENSE).

Using this tool to translate a sentence, the licence of the original sentence still applies unless specified otherwise.

Meaning, if you translate a sentence under [Creative Commons CC0](https://creativecommons.org/share-your-work/public-domain/cc0/), the translation is also under Creative Commons CC0.

Idem for any licence.