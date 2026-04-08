# Project Brief: web-cv-converter

## Overview

**Project:** web-cv-converter
**Type:** Web application — AI-powered CV/resume conversion to PDF
**Status:** Active development
**Repository:** AZANIR/web-cv-converter

## Goal

Convert Markdown CVs to polished PDFs using AI assistance. Users paste their Markdown CV and a job vacancy URL or text, the AI optimizes the CV content for the vacancy, and the result is rendered as a professional PDF for download.

## Core Features

- Markdown CV + vacancy input → AI optimization → PDF output
- Vacancy URL parsing (extracts job requirements)
- Conversion history and management per user
- Multiple professional CV templates
- Admin panel for user and email allowlist management
- Auth-gated: only approved emails can access

## Success Criteria

- End-to-end conversion completes in < 60 seconds
- Generated PDFs are professionally formatted
- Auth-protected: only `allowed_emails` table entries can log in
- System handles concurrent users without rate-limit errors
