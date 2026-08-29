# DESIGN.md — ResultScope UI direction

## Objective
Transform ResultScope from a chatbot assignment into a business-grade medical web app POC.

## Design inspiration
Use the interaction feel of a modern AI assistant in light mode:
- clean
- elegant
- calm
- product-like
- minimal but premium

Do NOT copy the Dribbble screen literally.
Use only high-level inspiration:
- light mode layout
- refined spacing
- strong hierarchy
- premium assistant feel
- soft rounded surfaces
- clear conversation flow

## Product identity
ResultScope is not a general chatbot.
It is a lab-intelligence web app.

The UI should communicate:
- laboratory result analysis
- trustworthy interpretation workflow
- educational medical context
- structured result explanation
- safe scope boundary

## Brand feel
- clinical
- modern
- calm
- premium
- English-first
- practical, not editorial
- not playful
- not startup-hype
- not robotic

## Visual rules
Avoid:
- dark mode
- glassmorphism
- neon gradients
- floating blobs
- generic AI sparkles
- cartoonish icons
- ChatGPT clone UI
- feature-card spam

Prefer:
- light background
- subtle panel contrast
- medical accent colors
- sans-serif hierarchy with a restrained mono data layer
- one primary intake panel, not a staged marketing sequence
- compact structured result views
- soft borders
- clean iconography
- mobile-first responsiveness

## Suggested palette
- background: warm off-white / very light gray
- surface: white
- text: deep slate
- muted text: cool gray
- primary accent: medical teal / blue-green
- secondary accent: soft cyan
- success/info accents: restrained green-blue
- danger/warning: muted clinical red/amber only when needed

## Layout
Desktop:
- left informational rail or top summary zone
- main analysis workspace
- structured input composer
- results/chat panel
- deterministic result summary visible

Mobile:
- single-column
- no cramped two-column layout
- sticky input actions if useful
- cards stack vertically
- maintain premium spacing and readability

## Core screens
1. Landing / intake state
   - concise English-first headline
   - structured textarea as the clear first action
   - compact examples below the intake
   - safety note without promotional process copy

2. Active analysis state
   - deterministic extracted values card
   - flagged values summary
   - AI interpretation panel
   - follow-up input
   - new analysis action

3. Out-of-scope state
   - calm refusal
   - explain lab-only boundary
   - offer example prompts

## Interaction rules
- user should feel like using a web app, not only a chat window
- first action = “Analyze result”
- keep chat for follow-up
- show symbolic/deterministic layer before AI narrative when available
- loading states should feel premium and calm
- errors should be product-like, not debug-like

## Accessibility
- responsive down to mobile width
- readable contrast
- clear focus states
- touch-friendly buttons
- avoid tiny text
