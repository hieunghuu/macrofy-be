# About This Project
This is a side project built to simulate a production-ready service and improve my DevOps skills. 

The codebase may not always follow the best practices, and there will likely be areas for improvement. 
If you notice better approaches, cleaner implementations, or architectural improvements, feel free to contribute or open a discussion.

# So why macrofy?

The thing is, I'm also a pretty hardcore gym rat, so the first thing I think about when choosing food is hitting my macros.

To be honest, there are already plenty of great nutrition tracking apps. Many of them even use AI to estimate calories and macros from a photo of your meal, so I don't see much value in competing in that space.

Also... I don't really want to pay for another subscription just to track my meals (I'm too cheap for that 😅).

Since I have a Computer Science background and now work in IT, I figured, why not build something that solves my own problem while keeping myself busy?

Alright, so i want to build something that solves my own problem: deciding what to eat. I'm often too lazy to think about different protein sources, and whenever I can't decide, the answer is always the same—rice and chicken, chicken with rice, rice next to chicken, or rice on top of chicken.

This project is about helping people discover meals that fit their nutrition goals, instead of just tracking what they've already eaten.

# Macrofy
One of three repos: `macrofy-be` (this one), `macrofy-fe`,
and `macrofy-ai`. This repo is a self-contained FastAPI service --
calculates TDEE and calorie targets from body stats + goals, and generates
meal plans from a curated meal catalog. All config is env-driven -- nothing
environment-specific is hardcoded.
