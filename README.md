# HyperX Lab Website

숭실대학교 HyperX Lab 홈페이지 (Jekyll + GitHub Pages).

## 내용 수정은 `_data/` 폴더에서

| 바꾸고 싶은 것 | 파일 |
|---|---|
| 홈 NEWS | `_data/news.yml` (맨 위에 추가) |
| 구성원 / 졸업생 | `_data/members.yml` (사진은 `assets/img/members/`) |
| 논문·특허 | `_data/publications.yml` |
| 과제 | `_data/projects.yml` |
| 강의 | `_data/lectures.yml` |
| 갤러리 | `_data/gallery.yml` (사진은 `assets/img/gallery/`) |
| 교수 소개 | `_data/professor.yml` |
| 연락처·주소·메뉴 | `_config.yml` |
| 홈 소개·모집 문구·연구분야 | `index.html` |
| 색상·디자인 | `assets/css/style.css` (맨 위 `:root` 변수) |

## 배포

GitHub 저장소 Settings → Pages → Source: `Deploy from a branch`, Branch: `main` / `(root)`.
저장소 이름이 `<사용자명>.github.io`가 아니면 `_config.yml`의 `baseurl`을 `"/<저장소명>"`으로 설정하세요.

## 로컬 미리보기 (선택)

```bash
gem install bundler jekyll
jekyll serve
```
