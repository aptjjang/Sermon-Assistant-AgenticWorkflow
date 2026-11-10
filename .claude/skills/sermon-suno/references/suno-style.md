# 수노 스타일 정하기

> 여기 적힌 수노 관련 내용은 대부분 **커뮤니티 경험칙(미검증)**이다. 2026년 11월 기준이며, 수노는 메뉴 이름과 모델이 자주 바뀐다.
> 실제로 확인된 결과는 `field-notes.md`에 적고, 그 기록이 이 파일보다 우선한다.

## 1. 수노에 넣는 것

| 칸 | 내용 | 언어 |
|---|---|---|
| Lyrics | 섹션 표시를 붙인 가사 | 한국어 |
| Style | 장르·분위기·악기·보컬·템포·편곡 곡선 | 영어 |
| Exclude | 빼고 싶은 것. **첫 생성은 비워 둔다.** 문제가 들리면 그때 넣는다 | 영어 |
| Title | 제목(= 후렴의 훅) | 한국어 |

**결과를 좌우하는 것은 태그가 아니라 가사의 모양이다**: 짧은 줄, 열린 모음, 같은 글자로 반복되는 후렴.

## 2. 갈래 먼저 고르기

블로그 글의 성격을 보고 둘 중 하나를 고른다. 사용자가 정해 주면 그대로 따른다.

| | 발라드 CCM (듣고 따라 부르는 찬양) | 회중 워십 (함께 부르는 찬양) |
|---|---|---|
| 맞는 글 | 위로·공감·한 사람의 이야기, 혼자 돌아보는 감사 | 선포·결단, 공동체가 함께 드리는 고백과 찬양 |
| 흐름 | 한 편의 극적 곡선. 클라이맥스는 브리지나 마지막 후렴 | 짧고 쉬운 후렴을 여러 번 반복 |
| 구조 | Intro → Verse 1 → Pre-Chorus → Chorus → Verse 2 → Pre-Chorus → Chorus → Bridge → Final Chorus → Outro → End | Intro → Verse 1 → Chorus → Verse 2 → Chorus → Bridge(2줄 반복) → Chorus → Final Chorus → Outro → End |
| 후렴 | 4줄 이하, 한 줄 5~9자 | 2~4줄, 한 줄 5~8자. 3번 이상 |
| 템포(추정) | 66~76 BPM | 느린 곡 72~80, 중간 80~100, 신나는 곡 125~145 |
| 마무리 | 마지막 후렴에서 반음 올리기(잘 안 될 수 있다 — §6) | 후렴 반복 뒤 제목 한 줄 |

- **갈래는 언제나 이 둘 중 하나**이고, 곡의 구조를 정한다. 소리(악기·분위기)는 §3의 출발점 문구가 정한다.
- 판단이 서지 않으면 **발라드 CCM**을 고른다. 2024~2026년에 가장 많이 불린 곡이 이 갈래다.
- 어느 갈래든 "처음 온 사람도 두 번째 후렴부터 따라 부른다"는 기준은 같다.

## 3. 글의 성격 → 스타일

글의 성격으로 갈래와 출발점 문구(§4)를 함께 고른다. 아래 값은 출발점(제안값)이다.

| 글의 성격 | 갈래(구조) | 출발점 문구 | 템포 | 악기 | 편곡 곡선 |
|---|---|---|---|---|---|
| 위로·동행 (광야, 혼자가 아님) | 발라드 CCM | 발라드 CCM | 68~74 | 피아노, 잔잔한 현악 | 절은 가까이 속삭이듯, 후렴에서 들어 올린다 |
| 감사·은혜 돌아보기 | 발라드 CCM | 어쿠스틱 고백 | 68~76 | 손으로 뜯는 어쿠스틱 기타, 첼로 | 느긋하게 가다가 마지막 후렴에서 살짝 들어 올린다 |
| 결단·헌신·부르심 | 회중 워십 | 회중 워십 | 76~88 | 피아노, 패드, 서서히 커지는 일렉 기타 | 천천히 쌓아 후렴에서 함께 부른다 |
| 묵상·기도 | 발라드 CCM | 발라드 CCM (현악을 뺀다) | 66~72 | 피아노 위주, 옅은 패드 | 끝까지 절제한다 |
| 탄식·기다림 | 발라드 CCM | 시네마틱 클라이맥스 | 66~70 | 피아노, 첼로 | 절제하다가 브리지나 마지막 후렴에서 소망이 들어온다 |
| 기쁨·찬양·축제 | 회중 워십 | 업템포 찬양 | 125~140 | 어쿠스틱 기타, 밴드 전체 | 밝고 힘 있게, 후렴을 크게 |

## 4. Style 문구 조립

**순서**: 장르 → 분위기 → 악기 2~3개 → 보컬 → 템포(BPM) → 편곡 곡선.

조립하는 법:

1. §3 표에서 고른 **출발점 문구**를 가져온다.
2. **BPM**을 표의 범위 가운데 값으로 바꾼다. `field-notes.md`에 확인된 값이 있으면 그 값을 쓴다.
3. **악기와 편곡 곡선**이 표와 다르면 바꿔 끼운다. 문구에 편곡 곡선이 없으면 한 구를 더한다(예: `gentle lift in final chorus`).
4. **보컬 표현**을 §5의 순서로 바꿔 끼운다.
5. 회중 워십이면 `singable mid-range melody`를 넣는다. 그 밖의 덧붙이는 구는 **첫 생성에는 넣지 않고**, 문제가 들리면 하나씩 넣는다(무엇이 효과였는지 알 수 있게).

- 쉼표로 이은 영어 구 8~10개 이내.
- **가수·팀 이름을 넣지 않는다.**
- '~없이' 같은 부정 표현은 Style이 아니라 **Exclude** 칸에 넣는다.
- 한 곡의 Style은 한 번 정하면 다시 생성할 때 바꾸지 않는다(무엇이 달라졌는지 비교할 수 있게).

### 출발점 문구

| 용도 | Style |
|---|---|
| 발라드 CCM | `Korean CCM ballad, emotional and tender, warm grand piano, soft strings, gentle acoustic guitar, clear Korean female vocal, 70 BPM, unhurried, intimate verses building to lifted chorus, strings enter only in final chorus` |
| 회중 워십 | `Korean contemporary worship, reverent and hopeful, piano and ambient pads, swelling electric guitar, heartfelt Korean male vocal, 76 BPM, slow build, congregational chorus, room ambience` |
| 어쿠스틱 고백 | `Korean acoustic CCM, folk-inflected, fingerpicked acoustic guitar, light cello, warm Korean male vocal, 68 BPM, laid-back delivery, breathing room between phrases, organic warm production` |
| 시네마틱 클라이맥스 | `Korean worship ballad, cinematic, piano and string ensemble, soft choir pads, Korean female vocal, 72 BPM, restrained verses, controlled orchestral lift in final chorus` |
| 업템포 찬양 (자료에 없는 제안) | `Korean contemporary worship, joyful and bright, acoustic guitar and full band, driving drums, energetic Korean mixed vocals, 130 BPM, big singable congregational chorus` |

| 덧붙일 수 있는 구 | 쓰임 |
|---|---|
| `Clear Korean pronunciation, natural Korean singing` | 발음 (효과 미검증) |
| `singable mid-range melody` | 회중이 부를 곡의 음역 |
| `half-step key change on final chorus` | 마지막 후렴 반음 올리기 (성공률 낮음) |

**Exclude에 넣을 수 있는 말** (문제가 들릴 때만): `rap, autotune, EDM drop, heavy distortion, English lyrics, spoken word`

## 5. 보컬

보컬은 이 순서로 정하고, 출발점 문구의 보컬 표현을 그에 맞게 바꿔 끼운다.

1. 사용자가 이번에 말한 것
2. `field-notes.md` '사용자가 정한 것'의 기본 보컬·고정 목소리
3. 둘 다 없으면 발라드 CCM은 여성(`clear Korean female vocal`), 회중 워십은 남성(`heartfelt Korean male vocal`). 조사 자료의 출발점 값일 뿐이므로 출력에 한 줄로 밝혀 바꿀 수 있게 한다

- 수노의 고정 목소리(Voices)는 음색만 유지하고 선율은 매번 새로 나온다.
- **남녀 두 판**을 요청하면 가사는 그대로 두고 Style의 보컬 표현만 바꾼다(그래야 두 판을 공정하게 비교한다). 남성판을 더 느리게 하려면 BPM 숫자를 낮추고 `unhurried`만 더한다.

## 6. 가사 칸의 태그

| 태그·기호 | 믿을 만한 정도 | 쓰는 법 |
|---|---|---|
| `[Intro]` `[Verse 1]` `[Pre-Chorus]` `[Chorus]` `[Bridge]` `[Outro]` `[End]` | 높음 | 섹션 앞 별도 줄에. `[End]`는 곡 끝의 군소리를 막는다 |
| `( )` 소괄호 | 높음 — **백보컬로 불린다** | 메아리·후창에만 쓴다. 발음 표기에는 쓰지 않는다 |
| `[Final Chorus]`, `[Verse: soft, intimate]` | 중간 | 편곡 곡선은 Style 끝에 적는 편이 낫다 |
| `[Male Vocal]` `[Female Vocal]` `[Choir]` | 중간 | Style에도 같은 보컬을 적어야 듣는다 |
| `[Key Change]`, 고음 지시, `[Whisper]` | 낮음 | 여러 번 생성해 고른다 |

- 섹션 표시가 아닌 연주 지시는 곡 전체에 8개 이내.
- 발음이 틀리면 태그나 괄호를 더하지 않고 **소리 나는 대로 한글을 고쳐 쓴다.**

### 가사 칸 모양

```text
[Intro]

[Verse 1]
(4줄)

[Pre-Chorus]
(1~2줄, 질문으로 끝)

[Chorus]
(4줄 이하, 제목이 첫 줄이나 끝 줄)

[Verse 2]
(4줄, 1절과 줄마다 같은 글자 수)

[Pre-Chorus]
(첫 프리코러스와 같은 가사)

[Chorus]
(첫 후렴과 글자 하나 다르지 않게)

[Bridge]
(2~4줄, 새 내용)

[Final Chorus]
(후렴 그대로, 한 줄에서 단어 하나만 바꾼다)

[Outro]
(제목 한 줄)

[End]
```

위에서 `(4줄)` 같은 소괄호는 설명이다. 실제 가사 칸에는 넣지 않는다(넣으면 불린다). `[Intro]`는 가사 없이 표시만 둔다.

## 7. 수노에서 만드는 순서

1. 정한 Style로 **2~4번** 생성한다. 같은 입력이라도 결과가 크게 다르다.
2. 가장 좋은 것을 고른다.
3. 어색한 줄이 있으면 `revision.md`를 따른다.
4. 길이가 모자라면 Extend로 잇는다.
5. 보컬이 밋밋하면 같은 입력으로 다른 모델 버전(v6 ↔ v5.5)을 비교한다.

## 8. 권리

- 기존 찬양의 가사나 선율을 넣지 않는다. 가수·팀 이름도 Style에 넣지 않는다.
- 무료 요금제로 만든 곡은 비상업용이고, 나중에 유료로 바꿔도 소급되지 않는다. 유료 요금제로 만든 곡에는 상업적 이용권이 주어진다. 요금제 조건은 바뀔 수 있으니 수노 사이트에서 확인하도록 안내한다.
