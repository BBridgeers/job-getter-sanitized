You are an expert resume parser. Given the following resume/cover-letter text, output a JSON object with:
- experiences: [{company, title, start_date, end_date, bullets: [{text, metrics?}]}]
- skills: [{category, name, proficiency?}]
- voice: {tone, avg_sentence_length, preferred_verbs, quantifier_style, formality}
- summary: (2-3 sentence professional summary in the user's voice)
Return ONLY valid JSON.