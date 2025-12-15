# 文件路径: api/index.py
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ---------------------------------------------------------
# 配置区
# 这里填你在第一步里获得的 Vercel 域名！
# 注意：不要带最后的斜杠 '/'
# ---------------------------------------------------------
NODE_API_URL = "http://1310621164-f4a6ohqzp0.ap-shanghai.tencentscf.com"

@app.route('/', methods=['GET', 'POST'])
def music_handler():
    # Vercel 有时会把参数放在 query string 里
    song_name = request.args.get('name')
    
    if not song_name:
        return jsonify({"code": 404, "msg": "歌名为空"})

    try:
        # --- 搜歌 ---
        # 这里的逻辑和之前一样，只是 NODE_API_URL 变成了云端地址
        search_url = f"{NODE_API_URL}/cloudsearch" 
        params = {'keywords': song_name, 'limit': 1}
        
        # 增加 headers 伪装，防止 Vercel 互相请求被拦截
        headers = {
            "User-Agent": "Mozilla/5.0 (WeChat-Music-Proxy)"
        }
        
        r = requests.get(search_url, params=params, headers=headers, timeout=10)
        data = r.json()
        
        songs = data.get('result', {}).get('songs')
        if not songs:
            return jsonify({"code": 404, "msg": "搜不到"})

        target_song = songs[0]
        song_id = target_song['id']
        title = target_song['name']
        ar_list = target_song.get('ar', []) or target_song.get('artists', [])
        artist = ar_list[0]['name'] if ar_list else "未知歌手"
        al = target_song.get('al', {}) or target_song.get('album', {})
        cover_url = al.get('picUrl', '')

        # --- 拿链接 ---
        url_api = f"{NODE_API_URL}/song/url"
        url_params = {'id': song_id}
        r_url = requests.get(url_api, params=url_params, headers=headers, timeout=10)
        url_data = r_url.json()
        
        music_url = ""
        if url_data.get('data'):
            music_url = url_data['data'][0]['url']
        
        if not music_url:
            music_url = f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

        # --- 返回 ---
        return jsonify({
            "code": 200,
            "title": title,
            "singer": artist,
            "cover": cover_url,
            "link": f"https://music.163.com/#/song?id={song_id}",
            "music_url": music_url
        })

    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})

# ⚠️ 注意：Vercel 环境下不需要 app.run()，也不能写 app.run()
# Vercel 会自动寻找 app 这个变量并运行它



