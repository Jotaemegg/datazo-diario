"""Descarga memes (Pixabay) y sonidos (Pixabay / Myinstants) a assets/. Uso: python fetch_assets.py"""
import os, subprocess
BASE = os.path.dirname(os.path.abspath(__file__))
PX = "https://cdn.pixabay.com/photo/"
MEMES = {
    "shock_gato": PX + "2020/03/07/07/07/cat-4908953_640.jpg",
    "grito_gato": PX + "2017/04/26/16/00/cat-2262916_640.jpg",
    "feliz_perro": PX + "2023/10/01/12/27/border-collie-8287329_640.jpg",
    "pensando_mono": PX + "2019/05/08/18/58/monkey-4189358_640.jpg",
    "sorprendido_mono": PX + "2016/02/12/23/49/monkey-1197100_640.jpg",
    "mirada_seria_gato": PX + "2014/03/29/09/17/cat-300572_640.jpg",
    "curioso_gato": PX + "2020/11/22/17/28/cat-5767334_640.jpg",
    "sospecha_perro": PX + "2022/05/09/18/05/dog-7185274_640.jpg",
    "triste_perro": PX + "2017/04/02/12/27/dogs-2195708_640.jpg",
    "enojado_gato": PX + "2016/03/27/22/22/face-1284513_640.jpg",
    "furioso_gato": PX + "2017/10/02/00/33/cat-2807517_640.jpg",
    "burlon_gato": PX + "2019/03/25/18/02/cat-4080907_640.jpg",
    "aburrido_gato": PX + "2016/11/29/13/52/cat-1870003_640.jpg",
    "desanimado_perro": PX + "2014/08/21/14/51/dog-423398_640.jpg",
}
PA = "https://cdn.pixabay.com/download/audio/"
MI = "https://www.myinstants.com/media/sounds/"
SFX = {
    "vine_boom": PA + "2025/08/29/audio_437b300d21.mp3?filename=bithuh-vine-boom-392646.mp3",
    "boing": PA + "2023/02/23/audio_be301496db.mp3?filename=universfield-cartoon-spring-boing-140378.mp3",
    "ding": PA + "2026/01/24/audio_d050f34e8a.mp3?filename=dragon-studio-correct-472358.mp3",
    "scratch_disco": PA + "2022/03/26/audio_7d318dd030.mp3?filename=freesound_community-record_scratch-108233.mp3",
    "risas_sitcom": PA + "2025/06/04/audio_ca6c7dfd22.mp3?filename=artificiallyinspired-90s-sitcom-laugh-track-353985.mp3",
    "huh_hombre": PA + "2025/06/02/audio_e1eaaa2f55.mp3?filename=universfield-confused-male-voice-huh-352694.mp3",
    "huh_gato": MI + "huh-cat-meme.mp3",
    "risa_gato": MI + "cat-laugh-meme-1.mp3",
    "faaah": MI + "faaah.mp3",
    "bruh": MI + "movie_1.mp3",
}
def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000: return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["curl", "-sS", "-L", "--max-time", "30", "-o", path, url], check=True)
for k, u in MEMES.items(): get(u, os.path.join(BASE, "assets", "memes", k + ".jpg"))
for k, u in SFX.items(): get(u, os.path.join(BASE, "assets", "sfx", k + ".mp3"))
print("assets ok")
