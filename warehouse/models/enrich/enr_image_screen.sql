-- Per product: how many of its images were screened and how many are clean
-- (no text, logo, watermark, border or child). Verdicts come from the cached
-- vision-model seed; a product with no clean screened image goes to review.
select
    i.pid,
    count(c.image_sha256)                        as images_screened,
    count(*) filter (where c.clean)              as images_clean,
    count(*) filter (where c.logo_or_brand)      as images_with_logo,
    count(*) filter (where c.text_overlay)       as images_with_text
from {{ ref('stg_cj_images') }} i
left join {{ ref('llm_image_screen_cache') }} c using (image_sha256)
group by i.pid
