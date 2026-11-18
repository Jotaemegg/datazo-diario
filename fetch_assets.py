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
    "dun_dun_dun": "https://cdn.pixabay.com/download/audio/2026/01/02/audio_9ded99071a.mp3",
    "suspenso": "https://cdn.pixabay.com/download/audio/2025/07/19/audio_0e2e7d4cb2.mp3",
    "ninos_woah": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_fa3b2a8c50.mp3",
    "publico_decepcion": "https://cdn.pixabay.com/download/audio/2025/06/02/audio_9dd11cb4aa.mp3",
    "aww": "https://cdn.pixabay.com/download/audio/2025/10/18/audio_4e48e9d4eb.mp3",
    "gasp": "https://cdn.pixabay.com/download/audio/2025/03/31/audio_98d8f51178.mp3",
    "tada": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_473a42432c.mp3",
    "caja_registradora": "https://cdn.pixabay.com/download/audio/2022/11/04/audio_7650b73fdb.mp3",
    "pop": "https://cdn.pixabay.com/download/audio/2025/09/09/audio_3023b9bde2.mp3",
    "error_buzzer": "https://cdn.pixabay.com/download/audio/2023/04/23/audio_65f312a7c6.mp3",
    "trombon_triste": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_c003cb2711.mp3",
    "aplausos": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_788f440de7.mp3",
    "silbato_slide": "https://cdn.pixabay.com/download/audio/2025/04/11/audio_7422833308.mp3",
    "bonk": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_7111d17a49.mp3",
    "reloj_tictac": "https://cdn.pixabay.com/download/audio/2025/06/10/audio_63b6707ae6.mp3",
    "camara": "https://cdn.pixabay.com/download/audio/2025/05/23/audio_c0a76b92b0.mp3",
    "redoble": "https://cdn.pixabay.com/download/audio/2021/08/09/audio_3b08dff96f.mp3",
    "glitch": "https://cdn.pixabay.com/download/audio/2025/07/24/audio_449f93605f.mp3",
    "riser": "https://cdn.pixabay.com/download/audio/2022/12/24/audio_74f3679d6a.mp3",
    "burbuja_pop": "https://cdn.pixabay.com/download/audio/2025/05/29/audio_145c0e7b22.mp3",
    "boom_dramatico": "https://cdn.pixabay.com/download/audio/2025/12/15/audio_11ae6bf966.mp3",
    "ninos_wow": "https://cdn.pixabay.com/download/audio/2025/11/25/audio_e406c5be77.mp3",
    "huh_pregunta": "https://cdn.pixabay.com/download/audio/2025/10/10/audio_d8b97f8382.mp3",
    "anime_wow": "https://www.myinstants.com/media/sounds/anime-wow-sound-effect.mp3",
    "oh_my_god": "https://www.myinstants.com/media/sounds/oh-my-god-meme.mp3",
    "yippee": "https://www.myinstants.com/media/sounds/yiipppeeee.mp3",
    "bocina_goofy": "https://www.myinstants.com/media/sounds/goofy-ahh-car-horn.mp3",
    "tubo_metal": "https://www.myinstants.com/media/sounds/metal-pipe-clang.mp3",
    "airhorn": "https://www.myinstants.com/media/sounds/mlg-airhorn.mp3",
    "dun_dun_brass": "https://www.myinstants.com/media/sounds/dun-dun-dun-sound-effect-brass_8nFBccR.mp3",
    "cachetada_oh": "https://www.myinstants.com/media/sounds/slap-oh_LGvkhyt.mp3",
    "violin_chirrido": "https://www.myinstants.com/media/sounds/violin-screech-meme.mp3",
    "what": "https://www.myinstants.com/media/sounds/what_JOcN7Y8.mp3",
    "run_vine": "https://www.myinstants.com/media/sounds/run-vine-sound-effect.mp3",
    "punch": "https://www.myinstants.com/media/sounds/punch-gaming-sound-effect-hd_RzlG1GE.mp3",
    "hueso_crack": "https://www.myinstants.com/media/sounds/bone-crack.mp3",
    "ronquido": "https://www.myinstants.com/media/sounds/snore-mimimimimimi.mp3",
    "buzzer_fuerte": "https://www.myinstants.com/media/sounds/extremely-loud-incorrect-buzzer_0cDaG20.mp3",
}
import re
def normalize(path):
    """Iguala el volumen de cada sonido (pico a -1 dB) para que ninguno suene muy bajo o muy fuerte."""
    out = subprocess.run(["ffmpeg", "-i", path, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"max_volume: ([-0-9.]+)", out)
    if not m: return
    gain = -1.0 - float(m.group(1))
    if abs(gain) < 0.5: return
    tmp = path[:-4] + ".norm.mp3"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", path, "-af", f"volume={gain}dB", tmp], check=True)
    os.replace(tmp, path)

def get(url, path, norm=False):
    if os.path.exists(path) and os.path.getsize(path) > 1000: return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["curl", "-sS", "-L", "--max-time", "30", "-o", path, url], check=True)
    if norm: normalize(path)
for k, u in MEMES.items(): get(u, os.path.join(BASE, "assets", "memes", k + ".jpg"))
for k, u in SFX.items(): get(u, os.path.join(BASE, "assets", "sfx", k + ".mp3"), norm=True)
print("assets ok")
