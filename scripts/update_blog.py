import requests
import git
import os

# 본인의 벨로그 아이디로 변경하세요
USERNAME = 'rtd7878' 

# 깃허브 레포지토리 경로
repo_path = '.'

def get_all_posts(username):
    """Velog GraphQL API를 사용하여 모든 글과 시리즈 정보를 가져옵니다."""
    query = """
    query Posts($cursor: ID, $username: String, $temp_only: Boolean, $tag: String, $limit: Int) {
      posts(cursor: $cursor, username: $username, temp_only: $temp_only, tag: $tag, limit: $limit) {
        id
        title
        body
        series {
          name
        }
      }
    }
    """
    posts = []
    cursor = None
    
    while True:
        variables = {
            "username": username,
            "limit": 100, # 한 번에 최대 100개씩 가져옴
            "cursor": cursor
        }
        
        response = requests.post(
            'https://v2.velog.io/graphql', 
            json={'query': query, 'variables': variables}
        )
        data = response.json()
        
        # 데이터가 없거나 에러가 발생하면 반복 종료
        if 'data' not in data or not data['data']['posts']:
            break
            
        fetched_posts = data['data']['posts']
        posts.extend(fetched_posts)
        
        # 가져온 글이 limit(100개)보다 작으면 마지막 페이지이므로 종료
        if len(fetched_posts) < 100:
            break
            
        # 다음 페이지를 위해 커서 업데이트
        cursor = fetched_posts[-1]['id']
        
    return posts

# 레포지토리 로드
repo = git.Repo(repo_path)

# 모든 포스트 가져오기
posts = get_all_posts(USERNAME)

for post in posts:
    # 파일 이름에서 유효하지 않은 문자 제거
    file_name = post['title'].replace('/', '-').replace('\\', '-') + '.md'
    
    # 시리즈 정보가 있으면 시리즈명으로 폴더 생성, 없으면 '미분류' 폴더 생성
    if post['series'] and post['series']['name']:
        series_name = post['series']['name'].replace('/', '-').replace('\\', '-')
        dir_path = os.path.join(repo_path, 'velog-posts', series_name)
    else:
        dir_path = os.path.join(repo_path, 'velog-posts', '미분류')
        
    # 폴더가 없다면 생성
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        
    file_path = os.path.join(dir_path, file_name)
    
    # 마크다운 본문 내용 (내용이 없을 경우 빈 문자열 처리)
    body = post['body'] if post['body'] else ""

    # 파일 작성
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(body)
        
    # 깃허브 add
    repo.git.add(file_path)

# 변경 사항이 있는지 확인 후 커밋 및 푸시
if repo.is_dirty() or repo.untracked_files:
    repo.git.commit('-m', 'Update Velog posts with Series')
    repo.git.push()
    print("성공적으로 Github에 업데이트 되었습니다.")
else:
    print("새롭게 업데이트할 내용이 없습니다.")
