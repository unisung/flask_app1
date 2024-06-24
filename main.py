# _*_ coding: utf-8 _*_

from flask import Flask, jsonify, render_template, request, make_response
import cv2
import base64
import numpy as np
import requests
import re
from deep_translator import GoogleTranslator

app = Flask(__name__)

# TMDB API 설정
TMDB_API_KEY = '119e4dc9f5f7b03f012b14d0c9c92598'
TMDB_POSTER_BASE_URL = 'https://image.tmdb.org/t/p/original'
TMDB_API_URL_SEARCH = f'https://api.themoviedb.org/3/search/movie'
TMDB_API_URL_MOVIE = f'https://api.themoviedb.org/3/movie/'

# Hugging Face API 설정
API_TOKEN = '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'
headers = {"Authorization": f"Bearer {API_TOKEN}"}
# 프레임으로 영화분류모델
API_URL = "https://api-inference.huggingface.co/models/dima806/movie_identification_by_frame"

# 번역
translator = GoogleTranslator(source='en', target='ko') # 구글 번역기 영어 -> 한글



@app.route('/')
def index():
  return render_template("index.html")

@app.route('/test1', methods=['GET', 'POST'])
def rest_api_test1():
  print(request.method)
  data = {"0": "0.01", "1": "0.99"}
  if request.method == 'GET':
    param = request.args.get('data')
    print(param)
    data.update({"param": param})
  elif request.method == 'POST':
    param = request.form.get('data')
    print(param)
    f = request.files['file']
    print(f.filename)
    f.save(f.filename)
    data.update({"param": param, "file": f.filename})
  #return jsonify(data)
  response = make_response(jsonify(data))
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response

@app.route('/test2', methods=['GET', 'POST'])
def rest_api_test2():
  print(request.method)
  data = {"0": "0.01", "1": "0.99"}
  if request.method == 'GET':
    param = request.args.get('data')
    print(param)
    data.update({"param": param})
  elif request.method == 'POST':
    param = request.form.get('data')
    print(param)
    f = request.files['file']
    print(f.filename)
    f.save(f.filename)
    data.update({"param": param, "file": f.filename})

  response = make_response(jsonify(data))
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response


#@app.route('/test_img', methods=['POST'])
@app.route('/analyze_img', methods=['POST'])
def rest_img_test():
  param = request.form.get('data')
  print(param)
  f = request.files['file']
  filestr = f.read()
  # FileStorage의 이미지를 넘파이 배열로 만듬
  npimg = np.frombuffer(filestr, np.uint8)
  # 넘파일 배열을 이미지 배열로 변환함
  img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
  cv2.imwrite(f.filename, img)
  # 여기에서 처리를 하면 됨 ##############
  # 이미지 파일로부터 영화 제목 가져오기
  image_path = f.filename
  #print(image_path)
  output = query(image_path)
  print('output:',output)

  # output = query1(img)
  #
  # 상위 3개의 결과 추출
  top_3_results = output[:3]

  # 각 결과에 대해 영화 정보 가져오기xx
  for result in top_3_results:
    predicted_title_with_year = result['label']
    predicted_title = extract_title_and_year(predicted_title_with_year)
    score = round(result['score'], 2)

    # TMDB에서 영화 정보 가져오기
    movie_info = get_movie_info(predicted_title)
    overview = movie_info['overview']
    # 번역
    translated_overview = translator.translate(overview)

    # 결과 출력
    if movie_info:
      print("영화 제목:", movie_info['title'])
      if movie_info['poster_url']:
        print("포스터 URL:", movie_info['poster_url'])
      else:
        print("포스터 URL을 찾을 수 없습니다.")
      print("개봉연도:", movie_info['release_date'])
      print("감독:", movie_info['director'])
      print("배우:", movie_info['actors'])
      print("장르:", ', '.join(movie_info['genres']))
      print("줄거리:", translated_overview)
      print("트레일러 링크:", movie_info['trailer_url'] if movie_info['trailer_url'] else "트레일러 없음")
      print(f"유사도:{(score * 100):.3f}%", )
      print("\n" + "=" * 50 + "\n")
    else:
      print(f"{predicted_title}에 대한 영화 정보를 찾을 수 없습니다.")
      print("\n" + "=" * 50 + "\n")


  ##############################################3
  img_str = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
  data = {"param": param, "file": img_str, "movie_info":movie_info,'overview':translated_overview}
  response = make_response(jsonify(data))
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response

## 이미지분류 관련 함수
# API에 이미지 파일 업로드하여 영화 제목 추출하는 함수
def query(filename):
#def query1(data):
    with open(filename, "rb") as f: #
        data = f.read()  #이미지파일 읽기
    response = requests.post(API_URL, headers=headers, data=data) #
    return response.json() # 응답 - json

# 응답 결과(제목(년도))에서 영화 제목과 년도를 분리하는 함수
def extract_title_and_year(title_with_year):
    match = re.match(r"(.+?) \(\d{4}\)", title_with_year)
    if match:
        return match.group(1) # 제목만 리턴
    return title_with_year

# TMDB에서 영화 정보 및 포스터 URL 가져오는 함수
def get_movie_info(movie_title): # 영화제목을 입력받아 영화정보 가져오는 함수
    params = {
        'api_key': TMDB_API_KEY,
        'query': movie_title
    }
    response = requests.get(TMDB_API_URL_SEARCH, params=params)
    data = response.json()
    if data['results']:
        movie_info = data['results'][0]
        movie_id = movie_info['id']
        # 추가 정보를 얻기 위해 개별 영화 API 호출
        movie_details_url = f'{TMDB_API_URL_MOVIE}{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits,videos'
        movie_details_response = requests.get(movie_details_url)
        movie_details = movie_details_response.json()

        # 감독 가져오기
        directors = [crew['name'] for crew in movie_details['credits']['crew'] if crew['department'] == 'Directing']
        # director = ", ".join(directors) if directors else "정보 없음"
        director = directors[0] if directors else "정보 없음"

        # 배우 가져오기 (상위 5명)
        cast = [actor['name'] for actor in movie_details['credits']['cast'][:5]]
        actors = ", ".join(cast) if cast else "정보 없음"

        # 트레일러 링크 가져오기 (첫 번째 트레일러만)
        trailer_url = ""
        if 'videos' in movie_details and movie_details['videos']['results']:
            trailer_key = movie_details['videos']['results'][0]['key']
            trailer_url = f"https://www.youtube.com/watch?v={trailer_key}"

        # 장르 가져오기
        genres = [genre['name'] for genre in movie_details.get('genres', [])]

        # 포스터 URL 구성
        poster_path = movie_info['poster_path']
        poster_url = TMDB_POSTER_BASE_URL + poster_path if poster_path else None

        return {
            'title': movie_info['title'],
            'poster_url': poster_url,
            'release_date': movie_info['release_date'],
            'director': director,
            'actors': actors,
            'genres': genres,
            'overview': movie_info['overview'],
            'trailer_url': trailer_url,
            'similarity': movie_info['popularity'] if 'popularity' in movie_info else None
        }
    else:
        return None



if __name__ == '__main__':
  app.debug = False
  app.run(host="127.0.0.1", port="5000")
  #app.run(host="0.0.0.0", port="5000")