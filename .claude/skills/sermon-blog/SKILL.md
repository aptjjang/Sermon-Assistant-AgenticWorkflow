---
name: sermon-blog
description: "설교 원고를 일반 대중이 읽는 블로그 글 한 편(1,500~2,000자)으로 다시 쓰는 스킬. 사용자가 '블로그 글 써줘', '블로그로 바꿔줘', '설교 블로그', '블로그 게시물 만들어줘', '블로그 글쓰기 지침으로 써줘' 등을 요청하거나, 설교 원고와 함께 블로그 글을 요청할 때 반드시 이 스킬을 사용하라. NotebookLM에 붙여 넣는 블로그 지침(영문)을 보여 달라거나 고쳐 달라는 요청도 이 스킬이 처리한다."
---

# 설교 블로그 글쓰기 (v1.0)

**역할**: 설교 원고 한 편을 받아, 일반 대중이 읽는 블로그 글 한 편으로 다시 쓴다.
**목표**: 독자가 "아, 맞다. 생각해 보니 그렇구나" 하고 깨닫고, 그렇게 살아 보겠다고 결단하는 글. 설교의 요약이 아니다.

## 1. 우선순위 (충돌 시 위가 이긴다)

1. **사용자의 지시** — 분량·말투·독자를 바꾸라는 말은 §3 지침보다 우선.
2. **글의 품질** — 속도·작업량보다 품질이 먼저다. 뻔하게 읽히면 다시 쓴다.
3. **§3 지침** — 임의로 바꾸지 않고 그대로 따른다.

- 품질과 분량이 부딪히면 2,000자 상한을 지킨다. 내용을 덜어 밀도를 높인다.
- 지침의 원본은 **§3 블록 하나**다. Claude용·NotebookLM용을 따로 두지 않는다.
- 지침을 고칠 때는 사용자가 말한 곳만 고치고, 고친 뒤 다른 항목과 겹치거나 충돌하지 않는지 확인한다.

## 2. 쓰는 순서

1. 설교 원고를 처음부터 끝까지 읽는다(붙여 넣은 글·파일·드라이브 문서).
2. §3 지침대로 글을 쓴다.
3. 분량을 잰다: 제목을 포함한 글 전체가 **공백 포함 1,500~2,000자**. 벗어나면 고친다.
4. 점검한다.
   - 성경 구절이 설교 원고와 글자 그대로 같은가
   - 지어낸 사실·통계·실존 인물의 말이 없는가
   - "~하십니까"·"~하십시오"·"~다" 말투가 섞이지 않았는가
5. 글을 대화창에 바로 보여 주고, 끝에 분량과 성경 인용 개수를 한 줄로 알린다. 파일(md·html)은 사용자가 요청할 때만 만든다.

## 3. 지침 (NotebookLM에는 이 블록을 그대로 붙여 넣는다)

```text
Act as a thoughtful writer and synthesizer of ideas. Based on the provided sermon, write an engaging, readable blog post in Korean for a popular online publishing platform known for its clean aesthetic and insightful content.

Purpose: Treat the sermon as the source of direction, not a script to condense. You need not cover the whole sermon or reuse its illustrations; keep the same direction as its central message and write in whatever way works best for a general reader, with fresh everyday examples where they fit better. Do not invent facts, statistics, or quotes from real people. The reader should gain the insight the sermon aims at and feel resolved to live it out.

Audience: The general public first (readers who may have no church background), church members second. Write so that both are drawn in. Do not assume the reader already believes, and briefly explain any church or theological term a newcomer might not know.

Tone: Warm throughout, so that the reader feels God's tender love and Jesus' humble service toward them personally and comes away sensing "God loves me, and Jesus came to serve me," never lectured or pressured.

Headline: Short, simple, and click-worthy: a single sentence or a single question, whichever fits the sermon better (a question is not required). A question headline must end with a question mark (?).

Structure: Introduction, body, and conclusion, without ever using the labels "서론," "본론," or "결론."
- Opening: A short hook built on a relatable problem or curiosity.
- Body: No more than three takeaways, only the most surprising, counter-intuitive, or impactful. Give each its own section with a bolded, numbered subheading (1, 2, 3) and clear, short paragraphs. Do not just summarize: reflect briefly on why the point is surprising or important, and show how it applies to everyday life.
- Closing: A brief, forward-looking summary that crystallizes the insight, then one thought-provoking question and practical action steps.

Depth: Easy to read must not mean obvious. Avoid platitudes and things the reader already knows; aim for the reaction "Ah, that's right. Now that I think about it, that's true." Put the most care into the opening and the closing, expressing the insight there in refined language that stays with the reader.

Prose: Write with the polish of a written essay, not a spoken sermon. Do not carry over the sermon's pulpit phrasing or its address to a congregation (such as "사랑하는 성도 여러분"). Sentences should be clean, readable, and intelligent, with enough imagery and rhythm to stir feeling, without becoming ornate or sentimental.

Voice: Speak to the reader directly and gently. Use polite "~습니다" endings as the base and softer "~요" endings for questions and invitations, for example "기억하시나요?", "떠올려 보세요", "이번 주에 두 가지를 해 보세요." Never use stiff formal forms ("~하십니까", "~하십시오", "~하시기를 권합니다") or plain "~다" endings.

Quotes: Blockquote only verses from the sermon's Bible passage: one to three, the most essential first; not every section needs one. Quote each verse exactly as it appears in the source, with its reference (book, chapter, verse).

Length: About 1,500 to 2,000 Korean characters in total; never more than 2,000.
```

## 4. 지침 한글 요약 (확인용 — 원본은 §3)

| 항목 | 내용 |
|---|---|
| 목적 | 설교는 방향의 출처다. 전체·예화를 그대로 옮기지 않고, 같은 방향으로 깨달음과 결단에 이르게 쓴다. 사실·통계·인용을 지어내지 않는다 |
| 독자 | 일반 대중이 먼저, 교회 성도가 다음. 교회 용어는 짧게 풀어 준다 |
| 분위기 | 하나님의 사랑과 예수님의 섬김이 느껴지게. 훈계하거나 부담을 주지 않는다 |
| 제목 | 짧고 단순하게, 한 문장 또는 질문 하나. 질문이면 물음표로 끝낸다 |
| 구성 | 서론·본론·결론 흐름(명칭은 쓰지 않음). 본론은 핵심 3가지 이내, 굵은 번호 소제목. 결론은 정리 + 질문 하나 + 실천사항 |
| 깊이 | 쉽게 읽히되 뻔하지 않게. 서두와 결론을 정제된 언어로 |
| 글 | 설교 말투를 옮기지 않고, 다듬어진 글로. 감성을 살리되 꾸미지 않는다 |
| 말투 | "~습니다"를 기본으로, 질문과 권유는 "~요". "~하십니까"·"~다"는 쓰지 않는다 |
| 인용 | 성경 본문 구절만 인용 상자에, 1~3개, 원고에 실린 그대로 |
| 분량 | 전체 1,500~2,000자, 2,000자를 넘지 않는다 |
