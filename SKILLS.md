# dev-bootstrap Skills Manifest

All 124 skills shipped with dev-bootstrap v0.1.0.
Each skill lives in its own directory: 'skill-name/SKILL.md'.
Installed at setup time to: %USERPROFILE%\.opencode\skills\ (follows junction if present).

---


## .system\skill-creator

- **skill-creator** - Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations.
  - path: '.system\skill-creator\SKILL.md'

## .system\skill-installer

- **skill-installer** - Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos).
  - path: '.system\skill-installer\SKILL.md'

## brainstorming

- **brainstorming** - You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.
  - path: 'brainstorming\SKILL.md'

## browser-act

- **browser-act** - Browser automation CLI (browser-act) for AI agents. MUST trigger when: (1) user mentions 'browser-act' in any form, or user needs to: (2) open/visit/browse/check a URL or webpage, (3) scrape/extract/crawl/monitor web content, (4) fill forms, click buttons, type text, scroll, or interact with page elements, (5) take a screenshot of a webpage, (6) handle or solve a captcha, (7) use a stealth/anti-detection browser or proxy, (8) connect to or control Chrome, (9) inspect network requests or record HAR, (10) automate any browser or web interaction task. Covers: navigation, page state inspection, element interaction, data extraction, JavaScript evaluation, tab management, network inspection, dialog handling, captcha solving, parallel browser sessions, stealth browsing, and any browser automation tasks.
  - path: 'browser-act\SKILL.md'

## crw

- **crw** - Scrape, crawl, map, and search the web using fastCRW. Use when the user needs web page content, site-wide extraction, URL discovery, or web search results. Single binary, 6 MB RAM, Firecrawl-compatible API.
  - path: 'crw\SKILL.md'

## dispatching-parallel-agents

- **dispatching-parallel-agents** - Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies
  - path: 'dispatching-parallel-agents\SKILL.md'

## ecc\agent-introspection-debugging

- **agent-introspection-debugging** - Structured self-debugging workflow for AI agent failures using capture, diagnosis, contained recovery, and introspection reports.
  - path: 'ecc\agent-introspection-debugging\SKILL.md'

## ecc\agent-sort

- **agent-sort** - Build an evidence-backed ECC install plan for a specific repo by sorting skills, commands, rules, hooks, and extras into DAILY vs LIBRARY buckets using parallel repo-aware review passes. Use when ECC should be trimmed to what a project actually needs instead of loading the full bundle.
  - path: 'ecc\agent-sort\SKILL.md'

## ecc\ai-regression-testing

- **ai-regression-testing** - Regression testing strategies for AI-assisted development. Sandbox-mode API testing without database dependencies, automated bug-check workflows, and patterns to catch AI blind spots where the same model writes and reviews code.
  - path: 'ecc\ai-regression-testing\SKILL.md'

## ecc\android-clean-architecture

- **android-clean-architecture** - Clean Architecture patterns for Android and Kotlin Multiplatform projects â€” module structure, dependency rules, UseCases, Repositories, and data layer patterns.
  - path: 'ecc\android-clean-architecture\SKILL.md'

## ecc\angular-developer

- **angular-developer** - Generates Angular code and provides architectural guidance. Trigger when creating projects, components, or services, or for best practices on reactivity (signals, linkedSignal, resource), forms, dependency injection, routing, SSR, accessibility (ARIA), animations, styling (component styles, Tailwind CSS), testing, or CLI tooling.
  - path: 'ecc\angular-developer\SKILL.md'

## ecc\api-design

- **api-design** - REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production APIs.
  - path: 'ecc\api-design\SKILL.md'

## ecc\backend-patterns

- **backend-patterns** - Backend architecture patterns, API design, database optimization, and server-side best practices for Node.js, Express, and Next.js API routes.
  - path: 'ecc\backend-patterns\SKILL.md'

## ecc\code-tour

- **code-tour** - Create CodeTour `.tour` files â€” persona-targeted, step-by-step walkthroughs with real file and line anchors. Use for onboarding tours, architecture walkthroughs, PR tours, RCA tours, and structured "explain how this works" requests.
  - path: 'ecc\code-tour\SKILL.md'

## ecc\coding-standards

- **coding-standards** - Baseline cross-project coding conventions for naming, readability, immutability, and code-quality review. Use detailed frontend or backend skills for framework-specific patterns.
  - path: 'ecc\coding-standards\SKILL.md'

## ecc\compose-multiplatform-patterns

- **compose-multiplatform-patterns** - Compose Multiplatform and Jetpack Compose patterns for KMP projects â€” state management, navigation, theming, performance, and platform-specific UI.
  - path: 'ecc\compose-multiplatform-patterns\SKILL.md'

## ecc\configure-ecc

- **configure-ecc** - Interactive installer for Everything Claude Code â€” guides users through selecting and installing skills and rules to user-level or project-level directories, verifies paths, and optionally optimizes installed files.
  - path: 'ecc\configure-ecc\SKILL.md'

## ecc\continuous-learning

- **continuous-learning** - [DEPRECATED - use continuous-learning-v2] Legacy v1 stop-hook skill extractor. v2 is a strict superset with instinct-based, project-scoped, hook-reliable learning. Do not invoke v1; route continuous learning, session learning, and pattern extraction requests to continuous-learning-v2.
  - path: 'ecc\continuous-learning\SKILL.md'

## ecc\continuous-learning-v2

- **continuous-learning-v2** - Instinct-based learning system that observes sessions via hooks, creates atomic instincts with confidence scoring, and evolves them into skills/commands/agents. v2.1 adds project-scoped instincts to prevent cross-project contamination.
  - path: 'ecc\continuous-learning-v2\SKILL.md'

## ecc\council

- **council** - Convene a four-voice council for ambiguous decisions, tradeoffs, and go/no-go calls. Use when multiple valid paths exist and you need structured disagreement before choosing.
  - path: 'ecc\council\SKILL.md'

## ecc\cpp-coding-standards

- **cpp-coding-standards** - C++ coding standards based on the C++ Core Guidelines (isocpp.github.io). Use when writing, reviewing, or refactoring C++ code to enforce modern, safe, and idiomatic practices.
  - path: 'ecc\cpp-coding-standards\SKILL.md'

## ecc\cpp-testing

- **cpp-testing** - Use only when writing/updating/fixing C++ tests, configuring GoogleTest/CTest, diagnosing failing or flaky tests, or adding coverage/sanitizers.
  - path: 'ecc\cpp-testing\SKILL.md'

## ecc\csharp-testing

- **csharp-testing** - C# and .NET testing patterns with xUnit, FluentAssertions, mocking, integration tests, and test organization best practices.
  - path: 'ecc\csharp-testing\SKILL.md'

## ecc\dart-flutter-patterns

- **dart-flutter-patterns** - Production-ready Dart and Flutter patterns covering null safety, immutable state, async composition, widget architecture, popular state management frameworks (BLoC, Riverpod, Provider), GoRouter navigation, Dio networking, Freezed code generation, and clean architecture.
  - path: 'ecc\dart-flutter-patterns\SKILL.md'

## ecc\django-patterns

- **django-patterns** - Django architecture patterns, REST API design with DRF, ORM best practices, caching, signals, middleware, and production-grade Django apps.
  - path: 'ecc\django-patterns\SKILL.md'

## ecc\django-tdd

- **django-tdd** - Django testing strategies with pytest-django, TDD methodology, factory_boy, mocking, coverage, and testing Django REST Framework APIs.
  - path: 'ecc\django-tdd\SKILL.md'

## ecc\django-verification

- **django-verification** - Verification loop for Django projects: migrations, linting, tests with coverage, security scans, and deployment readiness checks before release or PR.
  - path: 'ecc\django-verification\SKILL.md'

## ecc\dotnet-patterns

- **dotnet-patterns** - Idiomatic C# and .NET patterns, conventions, dependency injection, async/await, and best practices for building robust, maintainable .NET applications.
  - path: 'ecc\dotnet-patterns\SKILL.md'

## ecc\e2e-testing

- **e2e-testing** - Playwright E2E testing patterns, Page Object Model, configuration, CI/CD integration, artifact management, and flaky test strategies.
  - path: 'ecc\e2e-testing\SKILL.md'

## ecc\error-handling

- **error-handling** - Patterns for robust error handling across TypeScript, Python, and Go. Covers typed errors, error boundaries, retries, circuit breakers, and user-facing error messages.
  - path: 'ecc\error-handling\SKILL.md'

## ecc\eval-harness

- **eval-harness** - Formal evaluation framework for Claude Code sessions implementing eval-driven development (EDD) principles
  - path: 'ecc\eval-harness\SKILL.md'

## ecc\fastapi-patterns

- **fastapi-patterns** - FastAPI patterns for async APIs, dependency injection, Pydantic request and response models, OpenAPI docs, tests, security, and production readiness.
  - path: 'ecc\fastapi-patterns\SKILL.md'

## ecc\frontend-design-direction

- **frontend-design-direction** - Set an ECC-specific frontend design direction for production UI work. Use when building or improving websites, dashboards, applications, components, landing pages, visual tools, or any web UI that needs stronger product-specific design judgment.
  - path: 'ecc\frontend-design-direction\SKILL.md'

## ecc\frontend-patterns

- **frontend-patterns** - Frontend development patterns for React, Next.js, state management, performance optimization, and UI best practices.
  - path: 'ecc\frontend-patterns\SKILL.md'

## ecc\frontend-slides

- **frontend-slides** - Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when the user wants to build a presentation, convert a PPT/PPTX to web, or create slides for a talk/pitch. Helps non-designers discover their aesthetic through visual exploration rather than abstract choices.
  - path: 'ecc\frontend-slides\SKILL.md'

## ecc\fsharp-testing

- **fsharp-testing** - F# testing patterns with xUnit, FsUnit, Unquote, FsCheck property-based testing, integration tests, and test organization best practices.
  - path: 'ecc\fsharp-testing\SKILL.md'

## ecc\golang-patterns

- **golang-patterns** - Idiomatic Go patterns, best practices, and conventions for building robust, efficient, and maintainable Go applications.
  - path: 'ecc\golang-patterns\SKILL.md'

## ecc\golang-testing

- **golang-testing** - Go testing patterns including table-driven tests, subtests, benchmarks, fuzzing, and test coverage. Follows TDD methodology with idiomatic Go practices.
  - path: 'ecc\golang-testing\SKILL.md'

## ecc\hookify-rules

- **hookify-rules** - This skill should be used when the user asks to create a hookify rule, write a hook rule, configure hookify, add a hookify rule, or needs guidance on hookify rule syntax and patterns.
  - path: 'ecc\hookify-rules\SKILL.md'

## ecc\iterative-retrieval

- **iterative-retrieval** - Pattern for progressively refining context retrieval to solve the subagent context problem
  - path: 'ecc\iterative-retrieval\SKILL.md'

## ecc\java-coding-standards

- **java-coding-standards** - Java coding standards for Spring Boot and Quarkus services: naming, immutability, Optional usage, streams, exceptions, generics, CDI, reactive patterns, and project layout. Automatically applies framework-specific conventions.
  - path: 'ecc\java-coding-standards\SKILL.md'

## ecc\kotlin-coroutines-flows

- **kotlin-coroutines-flows** - Kotlin Coroutines and Flow patterns for Android and KMP â€” structured concurrency, Flow operators, StateFlow, error handling, and testing.
  - path: 'ecc\kotlin-coroutines-flows\SKILL.md'

## ecc\kotlin-exposed-patterns

- **kotlin-exposed-patterns** - JetBrains Exposed ORM patterns including DSL queries, DAO pattern, transactions, HikariCP connection pooling, Flyway migrations, and repository pattern.
  - path: 'ecc\kotlin-exposed-patterns\SKILL.md'

## ecc\kotlin-ktor-patterns

- **kotlin-ktor-patterns** - Ktor server patterns including routing DSL, plugins, authentication, Koin DI, kotlinx.serialization, WebSockets, and testApplication testing.
  - path: 'ecc\kotlin-ktor-patterns\SKILL.md'

## ecc\kotlin-patterns

- **kotlin-patterns** - Idiomatic Kotlin patterns, best practices, and conventions for building robust, efficient, and maintainable Kotlin applications with coroutines, null safety, and DSL builders.
  - path: 'ecc\kotlin-patterns\SKILL.md'

## ecc\kotlin-testing

- **kotlin-testing** - Kotlin testing patterns with Kotest, MockK, coroutine testing, property-based testing, and Kover coverage. Follows TDD methodology with idiomatic Kotlin practices.
  - path: 'ecc\kotlin-testing\SKILL.md'

## ecc\laravel-patterns

- **laravel-patterns** - Laravel architecture patterns, routing/controllers, Eloquent ORM, service layers, queues, events, caching, and API resources for production apps.
  - path: 'ecc\laravel-patterns\SKILL.md'

## ecc\laravel-plugin-discovery

- **laravel-plugin-discovery** - Discover and evaluate Laravel packages via LaraPlugins.io MCP. Use when the user wants to find plugins, check package health, or assess Laravel/PHP compatibility.
  - path: 'ecc\laravel-plugin-discovery\SKILL.md'

## ecc\laravel-tdd

- **laravel-tdd** - Test-driven development for Laravel with PHPUnit and Pest, factories, database testing, fakes, and coverage targets.
  - path: 'ecc\laravel-tdd\SKILL.md'

## ecc\laravel-verification

- **laravel-verification** - Verification loop for Laravel projects: env checks, linting, static analysis, tests with coverage, security scans, and deployment readiness.
  - path: 'ecc\laravel-verification\SKILL.md'

## ecc\make-interfaces-feel-better

- **make-interfaces-feel-better** - Apply concrete design-engineering details that make interfaces feel polished. Use when reviewing or improving UI spacing, typography, borders, shadows, motion, hit areas, icons, text wrapping, and interaction states.
  - path: 'ecc\make-interfaces-feel-better\SKILL.md'

## ecc\mcp-server-patterns

- **mcp-server-patterns** - Build MCP servers with Node/TypeScript SDK â€” tools, resources, prompts, Zod validation, stdio vs Streamable HTTP. Use Context7 or official MCP docs for latest API.
  - path: 'ecc\mcp-server-patterns\SKILL.md'

## ecc\motion-ui

- **motion-ui** - Production-ready UI motion system for React/Next.js. Use when implementing animations, transitions, or motion patterns.
  - path: 'ecc\motion-ui\SKILL.md'

## ecc\nestjs-patterns

- **nestjs-patterns** - NestJS architecture patterns for modules, controllers, providers, DTO validation, guards, interceptors, config, and production-grade TypeScript backends.
  - path: 'ecc\nestjs-patterns\SKILL.md'

## ecc\perl-patterns

- **perl-patterns** - Modern Perl 5.36+ idioms, best practices, and conventions for building robust, maintainable Perl applications.
  - path: 'ecc\perl-patterns\SKILL.md'

## ecc\perl-testing

- **perl-testing** - Perl testing patterns using Test2::V0, Test::More, prove runner, mocking, coverage with Devel::Cover, and TDD methodology.
  - path: 'ecc\perl-testing\SKILL.md'

## ecc\plankton-code-quality

- **plankton-code-quality** - Write-time code quality enforcement using Plankton â€” auto-formatting, linting, and Claude-powered fixes on every file edit via hooks.
  - path: 'ecc\plankton-code-quality\SKILL.md'

## ecc\production-audit

- **production-audit** - Local-evidence production readiness audit for shipped apps, pre-launch reviews, post-merge checks, and "what breaks in prod?" questions without sending repo data to an external audit service.
  - path: 'ecc\production-audit\SKILL.md'

## ecc\python-patterns

- **python-patterns** - Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications.
  - path: 'ecc\python-patterns\SKILL.md'

## ecc\python-testing

- **python-testing** - Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements.
  - path: 'ecc\python-testing\SKILL.md'

## ecc\quarkus-patterns

- **quarkus-patterns** - Quarkus 3.x LTS architecture patterns with Camel for messaging, RESTful API design, CDI services, data access with Panache, and async processing. Use for Java Quarkus backend work with event-driven architectures.
  - path: 'ecc\quarkus-patterns\SKILL.md'

## ecc\quarkus-tdd

- **quarkus-tdd** - Test-driven development for Quarkus 3.x LTS using JUnit 5, Mockito, REST Assured, Camel testing, and JaCoCo. Use when adding features, fixing bugs, or refactoring event-driven services.
  - path: 'ecc\quarkus-tdd\SKILL.md'

## ecc\quarkus-verification

- **quarkus-verification** - Verification loop for Quarkus projects: build, static analysis, tests with coverage, security scans, native compilation, and diff review before release or PR.
  - path: 'ecc\quarkus-verification\SKILL.md'

## ecc\react-patterns

- **react-patterns** - React 18/19 patterns including hooks discipline, server/client component boundaries, Suspense + error boundaries, form actions, data fetching, state management decision trees, and accessibility-first composition. Use when writing or reviewing React components.
  - path: 'ecc\react-patterns\SKILL.md'

## ecc\react-performance

- **react-performance** - React and Next.js performance optimization patterns adapted from Vercel Engineering's React Best Practices (https://github.com/vercel-labs/agent-skills). Organizes 70+ rules across 8 priority categories â€” waterfalls, bundle size, server-side, client fetching, re-render, rendering, JS micro-perf, advanced. Use when writing, reviewing, or refactoring React/Next.js code for performance.
  - path: 'ecc\react-performance\SKILL.md'

## ecc\react-testing

- **react-testing** - React component testing with React Testing Library, Vitest/Jest, MSW for network mocking, accessibility assertions with axe, and the decision boundary between component tests and Playwright/Cypress end-to-end runs. Use when writing or fixing tests for React components, hooks, or pages.
  - path: 'ecc\react-testing\SKILL.md'

## ecc\rust-patterns

- **rust-patterns** - Idiomatic Rust patterns, ownership, error handling, traits, concurrency, and best practices for building safe, performant applications.
  - path: 'ecc\rust-patterns\SKILL.md'

## ecc\rust-testing

- **rust-testing** - Rust testing patterns including unit tests, integration tests, async testing, property-based testing, mocking, and coverage. Follows TDD methodology.
  - path: 'ecc\rust-testing\SKILL.md'

## ecc\skill-scout

- **skill-scout** - Search existing local, marketplace, GitHub, and web skill sources before creating a new skill. Use when the user wants to create, build, fork, or find a skill for a workflow.
  - path: 'ecc\skill-scout\SKILL.md'

## ecc\skill-stocktake

- **skill-stocktake** - Use when auditing Claude skills and commands for quality. Supports Quick Scan (changed skills only) and Full Stocktake modes with sequential subagent batch evaluation.
  - path: 'ecc\skill-stocktake\SKILL.md'

## ecc\springboot-patterns

- **springboot-patterns** - Spring Boot architecture patterns, REST API design, layered services, data access, caching, async processing, and logging. Use for Java Spring Boot backend work.
  - path: 'ecc\springboot-patterns\SKILL.md'

## ecc\springboot-tdd

- **springboot-tdd** - Test-driven development for Spring Boot using JUnit 5, Mockito, MockMvc, Testcontainers, and JaCoCo. Use when adding features, fixing bugs, or refactoring.
  - path: 'ecc\springboot-tdd\SKILL.md'

## ecc\springboot-verification

- **springboot-verification** - Verification loop for Spring Boot projects: build, static analysis, tests with coverage, security scans, and diff review before release or PR.
  - path: 'ecc\springboot-verification\SKILL.md'

## ecc\strategic-compact

- **strategic-compact** - Suggests manual context compaction at logical intervals to preserve context through task phases rather than arbitrary auto-compaction.
  - path: 'ecc\strategic-compact\SKILL.md'

## ecc\tdd-workflow

- **tdd-workflow** - Use this skill when writing new features, fixing bugs, or refactoring code. Enforces test-driven development with 80%+ coverage including unit, integration, and E2E tests.
  - path: 'ecc\tdd-workflow\SKILL.md'

## ecc\ui-to-vue

- **ui-to-vue** - Use when the user has UI screenshots or design exports that need batch conversion into Vue 3 components, especially with Vant, Element Plus, or Ant Design Vue.
  - path: 'ecc\ui-to-vue\SKILL.md'

## ecc\verification-loop

- **verification-loop** - A comprehensive verification system for Claude Code sessions.
  - path: 'ecc\verification-loop\SKILL.md'

## ecc\windows-desktop-e2e

- **windows-desktop-e2e** - E2E testing for Windows native desktop apps (WPF, WinForms, Win32/MFC, Qt) using pywinauto and Windows UI Automation.
  - path: 'ecc\windows-desktop-e2e\SKILL.md'

## executing-plans

- **executing-plans** - Use when you have a written implementation plan to execute in a separate session with review checkpoints
  - path: 'executing-plans\SKILL.md'

## finishing-a-development-branch

- **finishing-a-development-branch** - Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup
  - path: 'finishing-a-development-branch\SKILL.md'

## receiving-code-review

- **receiving-code-review** - Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation
  - path: 'receiving-code-review\SKILL.md'

## requesting-code-review

- **requesting-code-review** - Use when completing tasks, implementing major features, or before merging to verify work meets requirements
  - path: 'requesting-code-review\SKILL.md'

## scrapling

- **scrapling** - Adaptive web scraping framework with anti-bot bypass and spider crawling. Use when asked to scrape, crawl, or extract data from websites; web_fetch fails; the site has anti-bot protections; write Python code to scrape/crawl; or write spiders. Requires Python 3.10+.
  - path: 'scrapling\SKILL.md'

## solutions\ecommerce\amazon-asin-lookup-api-skill

- **amazon-asin-lookup-api-skill** - This skill helps users extract structured product details from Amazon using a specific ASIN (Amazon Standard Identification Number). Use this skill when the user asks to get Amazon product details by ASIN, lookup Amazon product title and price using ASIN, extract Amazon product ratings and reviews count for a specific ASIN, check Amazon product availability and current price, get Amazon product description and features via ASIN, enrich product catalog with Amazon data using ASIN, monitor Amazon product price changes for specific ASINs, retrieve Amazon product brand and material information, fetch Amazon product images and specifications by ASIN, validate Amazon ASIN and get product metadata.
  - path: 'solutions\ecommerce\amazon-asin-lookup-api-skill\SKILL.md'

## solutions\ecommerce\amazon-best-selling-products-finder-api-skill

- **amazon-best-selling-products-finder-api-skill** - This skill helps users extract structured best-selling product data from Amazon via the BrowserAct API. Agent should proactively apply this skill when users express needs like search for best selling products on Amazon, extract Amazon product data based on keywords, find top rated Amazon products, monitor Amazon competitor prices and sales, discover trending products on Amazon marketplace, extract Amazon product titles prices and ratings, gather Amazon product sales volume for market research, search Amazon best sellers in specific region, collect Amazon product reviews and promotion details, analyze Amazon product availability and badges, get Amazon product data for market analysis.
  - path: 'solutions\ecommerce\amazon-best-selling-products-finder-api-skill\SKILL.md'

## solutions\ecommerce\amazon-buy-box-monitor-api-skill

- **amazon-buy-box-monitor-api-skill** - This skill helps users extract basic product details other sellers prices and seller ratings from Amazon via ASIN automatically using the BrowserAct API. Agent should proactively apply this skill when users express needs like query Amazon buy box information, monitor Amazon product prices, extract Amazon product details by ASIN, check other sellers prices on Amazon, get Amazon seller ratings and feedback count, monitor buy box ownership for a specific ASIN, track Amazon fulfillment methods for competitors, compare Amazon product prices across different sellers, retrieve Amazon buy box availability status, analyze Amazon seller profile details.
  - path: 'solutions\ecommerce\amazon-buy-box-monitor-api-skill\SKILL.md'

## solutions\ecommerce\amazon-competitor-analyzer

- **amazon-competitor-analyzer** - Scrapes Amazon product data from ASINs using browseract.com automation API and performs surgical competitive analysis. Compares specifications, pricing, review quality, and visual strategies to identify competitor moats and vulnerabilities.
  - path: 'solutions\ecommerce\amazon-competitor-analyzer\SKILL.md'

## solutions\ecommerce\amazon-listing-competitor-analysis-skill

- **amazon-listing-competitor-analysis-skill** - This skill helps users analyze Amazon competitor listings by ASIN and produce structured competitive intelligence plus strategic opportunity points for their own go-to-market. The Agent should proactively apply this skill when users want to analyze a competitor Amazon listing by ASIN, understand what a top-ranked product does right in content keywords or visuals, find market gaps and unmet buyer needs, turn competitor research into opportunity maps for their brand, identify keyword placement patterns on rival listings, extract SEO insights from Amazon product pages, reverse-engineer competitor bullet and title strategies, mine competitor reviews for buyer psychology, compare seller and A plus content patterns, run gap analysis before launching a new SKU, research why a listing wins conversion signals, synthesize whitespace you can own versus the diagnosed listing, or say just look at this ASIN with a competitive or optimization angle.
  - path: 'solutions\ecommerce\amazon-listing-competitor-analysis-skill\SKILL.md'

## solutions\ecommerce\amazon-product-api-skill

- **amazon-product-api-skill** - This skill helps users extract structured product listings from Amazon, including titles, ASINs, prices, ratings, and specifications. Use this skill when users want to search for products on Amazon, find the best selling brand products, track price changes for items, get a list of categories with high ratings, compare different brand products on Amazon, extract Amazon product data for market research, look for products in a specific language or marketplace, analyze competitor pricing for keywords, find featured products for search terms, get technical specifications like material or color for product lists.
  - path: 'solutions\ecommerce\amazon-product-api-skill\SKILL.md'

## solutions\ecommerce\amazon-product-search-api-skill

- **amazon-product-search-api-skill** - This skill is designed to help users automatically extract product data from Amazon search results. The Agent should proactively apply this skill when users request searching for products related to keywords, finding best-selling items from specific brands, monitoring product prices and availability on Amazon, extracting product listings for market research, collecting product ratings and review counts for competitive analysis, finding specific products with a maximum count, searching Amazon in different languages for localized results, tracking monthly sales estimates for brand products, gathering product URLs and titles for a product catalog, scanning Amazon for Best Seller tags in a specific category, monitoring shipping and delivery information for brand items, building a structured dataset of Amazon search results.
  - path: 'solutions\ecommerce\amazon-product-search-api-skill\SKILL.md'

## solutions\ecommerce\amazon-reviews-api-skill

- **amazon-reviews-api-skill** - This skill helps users automatically extract Amazon product reviews via the Amazon Reviews API. Agent should proactively apply this skill when users express needs like getting reviews for Amazon product with ASIN B07TS6R1SF, analyzing customer feedback for a specific Amazon item, getting ratings and comments for a competitive product, tracking sentiment of recent Amazon reviews, extracting verified purchase reviews for quality assessment, summarizing user experiences from Amazon product pages, monitoring product performance through customer reviews, collecting reviewer profiles and links for market research, gathering review titles and descriptions for content analysis, scraping Amazon reviews without requiring a login.
  - path: 'solutions\ecommerce\amazon-reviews-api-skill\SKILL.md'

## solutions\lead-generation\business-contact-social-links-skill

- **business-contact-social-links-skill** - This skill helps users automatically extract official website and social media profiles. Agent should proactively apply this skill when users express needs like search for official website and social media contacts of a company, find YouTube and LinkedIn profiles by company name, extract social media links from a specific website URL, discover a company's X and Facebook presence, gather business contact details using their brand name, retrieve TikTok and Instagram links from a target website, track competitor social media strategy, extract multi-platform social links for lead generation, find official contact channels of local businesses, collect canonical profile URLs for outreach campaigns, or build a contact database from Yellow Pages leads.
  - path: 'solutions\lead-generation\business-contact-social-links-skill\SKILL.md'

## solutions\lead-generation\github-project-contributor-finder-api-skill

- **github-project-contributor-finder-api-skill** - This skill helps users extract GitHub repository project details and contributor contact information using keywords, stars, and update dates. Agent should proactively apply this skill when users express needs like search for GitHub projects by keywords, find top open-source contributors in specific domains, extract developer contacts from GitHub repositories, discover trending repositories with high stars, gather contributor profiles and social links for tech recruiting, retrieve GitHub project descriptions and metrics, build developer communities by finding active contributors, search for repositories updated recently, collect personal website and Twitter links of developers, generate targeted leads for developer tools, or track active open-source contributors for collaboration.
  - path: 'solutions\lead-generation\github-project-contributor-finder-api-skill\SKILL.md'

## solutions\lead-generation\google-maps-api-skill

- **google-maps-api-skill** - This skill helps users automatically scrape business data from Google Maps using the BrowserAct Google Maps API. Agent should proactively trigger this skill for needs like finding restaurants in a specific city, extracting contact info of dental clinics, researching local competitors, collecting addresses of coffee shops, generating lead lists for specific industries, monitoring business ratings and reviews, getting opening hours of local services, finding specialized stores (e.g., Turkish-style restaurants), analyzing business categories in a region, extracting website links from local businesses, gathering phone numbers for sales outreach, mapping out service providers in a specific country.
  - path: 'solutions\lead-generation\google-maps-api-skill\SKILL.md'

## solutions\lead-generation\google-maps-reviews-api-skill

- **google-maps-reviews-api-skill** - This skill is designed to help users automatically extract reviews from Google Maps via the Google Maps Reviews API. Agent should proactively apply this skill when users request to find reviews for local businesses (e.g., coffee shops, clinics), monitor customer feedback for a specific brand or location, analyze sentiment of reviews for competitors, extract reviews for a chain of stores or services, track reputation of a local restaurant, gather user testimonials for a specific venue, conduct market research on service quality of local businesses, monitor reviews for a new retail location, collect feedback on public attractions or parks, identify common complaints for a specific service provider, research the best-rated places in a city, analyze recurring themes in reviews for a specific industry.
  - path: 'solutions\lead-generation\google-maps-reviews-api-skill\SKILL.md'

## solutions\lead-generation\google-maps-search-api-skill

- **google-maps-search-api-skill** - This skill is designed to help users automatically extract business data from Google Maps search results. The Agent should proactively apply this skill when the user makes the following requests searching for coffee shops in a specific city, finding dentists or medical clinics nearby, tracking competitors' locations in a certain area, extracting business leads from Google Maps lists, gathering restaurant data for market research, finding hotels or accommodation options in a region, locating specific services like coworking spaces or gyms, monitoring new business openings in a neighborhood, collecting contact information and addresses for sales prospecting, analyzing price ranges and cuisines of local eateries, getting ratings and review counts for a list of businesses, exporting local business data into a CRM or database.
  - path: 'solutions\lead-generation\google-maps-search-api-skill\SKILL.md'

## solutions\lead-generation\industry-key-contact-radar-api-skill

- **industry-key-contact-radar-api-skill** - This skill helps users discover key contacts across industries, roles, and social platforms via the BrowserAct API. Agent should proactively apply this skill when users express needs like finding public profiles for founders or CEOs, discovering key decision-makers in a specific industry, extracting contact details for lead generation, searching for growth leaders on LinkedIn or Facebook, gathering professional networking profiles, retrieving URLs and names of industry leaders, finding marketing managers in a specific field, conducting competitive analysis by identifying key personnel, sourcing talent acquisition targets across platforms, or compiling a list of target roles on specific social sites.
  - path: 'solutions\lead-generation\industry-key-contact-radar-api-skill\SKILL.md'

## solutions\lead-generation\social-media-finder-skill

- **social-media-finder-skill** - This skill helps users automatically find social media profiles across platforms like Facebook, Twitter, Instagram, LinkedIn, etc. using the BrowserAct API. Agent should proactively apply this skill when users express needs like finding someone's social media accounts, discovering a brand's social media presence, tracking down social profiles of job candidates, finding contact info for sales prospects, researching a person's digital footprint, verifying the identity of someone met online, monitoring the social media reach of influencers, checking social accounts of business competitors, gathering public profiles for background research, locating official customer service accounts across platforms, or compiling contact databases for networking.
  - path: 'solutions\lead-generation\social-media-finder-skill\SKILL.md'

## solutions\search-research\google-image-api-skill

- **google-image-api-skill** - This skill helps users automatically extract structured image data from Google Images via BrowserAct API. Agent should proactively apply this skill when users express needs like finding images for specific keywords, gathering product style images for competitors, building visual datasets at scale, scanning visual search results for market research, tracking localized image trends by country, compiling related image thumbnails and links, extracting image titles and source logos, fetching click through URLs from image results, monitoring competitor visual assets, sourcing creative content for specific topics, looking up product pictures in different regions, collecting structured image metadata without opening detail pages.
  - path: 'solutions\search-research\google-image-api-skill\SKILL.md'

## solutions\search-research\google-news-api-skill

- **google-news-api-skill** - This skill helps users automatically extract structured news data from Google News via BrowserAct API. Agent should proactively apply this skill when users express needs like searching for news about a specific topic, tracking industry trends, monitoring public relations or sentiment, collecting competitor updates, getting latest reports on specific keywords, monitoring brand exposure in media, researching market hot topics, summarizing daily industry news, tracking media activities of specific individuals, retrieving hot events from the past 24 hours, extracting structured data for market research, monitoring global breaking news.
  - path: 'solutions\search-research\google-news-api-skill\SKILL.md'

## solutions\search-research\web-research-assistant

- **web-research-assistant** - AI-powered web research assistant that leverages BrowserAct API to supplement restricted web access by searching the internet for additional information. Designed for OpenClaw and Claude Code.
  - path: 'solutions\search-research\web-research-assistant\SKILL.md'

## solutions\search-research\web-search-scraper-api-skill

- **web-search-scraper-api-skill** - This skill helps users automatically extract complete Markdown content from any website via the BrowserAct Web Search Scraper API. The Agent should proactively apply this skill when users express needs like extract complete markdown from a specific website, scrape the content of an article link, get the text from a target url, convert a webpage to markdown format, fetch the main content of a blog post, extract data from a given web page, parse the html of a website into markdown, download the readable text from a news article, obtain the content of a tutorial page, extract all the markdown text from any http or https url, scrape documentation from a web link, or grab the text of a single webpage.
  - path: 'solutions\search-research\web-search-scraper-api-skill\SKILL.md'

## solutions\social-listening\reddit-competitor-analysis-api-skill

- **reddit-competitor-analysis-api-skill** - This skill helps users extract structured data from Reddit posts and comments via BrowserAct API. Agent should proactively apply this skill when users express needs like analyzing competitor mentions on Reddit, tracking brand sentiment in Reddit comments, extracting Reddit discussions for market research, finding popular Reddit posts by keywords, monitoring community feedback on specific topics, gathering user reviews from Reddit threads, searching for Reddit posts within a specific date range, sorting Reddit discussions by relevance or hotness, compiling nested Reddit comments for deep analysis, building a structured dataset of Reddit conversations, discovering trending topics in specific subreddits, or monitoring social media activity for specific brands on Reddit.
  - path: 'solutions\social-listening\reddit-competitor-analysis-api-skill\SKILL.md'

## solutions\social-listening\wechat-article-search-api-skill

- **wechat-article-search-api-skill** - This skill helps users extract full article contents from WeChat using the BrowserAct API. The Agent should proactively apply this skill when users express needs like finding full WeChat articles for specific keywords, tracking WeChat public accounts for industry trends, extracting WeChat article contents for media research, monitoring public relations on WeChat platforms, collecting competitor updates from WeChat, getting full article body from WeChat links, monitoring brand exposure on WeChat articles, retrieving structured WeChat data for sentiment analysis, summarizing daily news from WeChat, getting author and publication date for WeChat articles, or automating WeChat content extraction without scraping.
  - path: 'solutions\social-listening\wechat-article-search-api-skill\SKILL.md'

## solutions\social-listening\zhihu-search-api-skill

- **zhihu-search-api-skill** - This skill helps users automatically extract structured article details and full content from Zhihu via the BrowserAct API. Agent should proactively apply this skill when users express needs like: searching for Zhihu articles on a specific topic, tracking industry trends on Zhihu, monitoring public relations or sentiment on Zhihu, collecting competitor updates, getting the latest reports on specific keywords, monitoring brand exposure in Zhihu media, researching market hot topics, summarizing daily Zhihu industry news, retrieving hot events from the past week, extracting structured data for market research, finding full Zhihu articles for AI agents, extracting full article body from Zhihu links.
  - path: 'solutions\social-listening\zhihu-search-api-skill\SKILL.md'

## solutions\video-platforms\youtube-api-skill

- **youtube-api-skill** - This skill helps users automatically extract detailed video metrics and channel information from YouTube based on keyword searches using the BrowserAct API. The Agent should proactively apply this skill when users express needs such as extract specific keyword YouTube video detailed data, monitor the latest video performance of competitor channels, collect comment and like counts for videos on a specific topic, find AI agent tutorials published this week and extract metrics, evaluate total views and subscriber info for specific videos, scrape detailed metrics of marketing campaign videos, track video trends for a tech topic periodically, get high quality video list data for specified keywords on YouTube, mine detailed information of the latest YouTube videos, collect video duration and engagement data for specific industries, or monitor YouTube content creator performance metrics.
  - path: 'solutions\video-platforms\youtube-api-skill\SKILL.md'

## solutions\video-platforms\youtube-batch-transcript-extractor-api-skill

- **youtube-batch-transcript-extractor-api-skill** - This skill helps users automatically extract YouTube video transcripts and metadata in batch via the BrowserAct API. The Agent should proactively apply this skill when users express needs like batch extract full transcripts from YouTube videos for specific keywords, scrape YouTube subtitles for a list of videos, get batch video metadata and likes counts for analysis, automate YouTube search and subtitle extraction, collect multiple video transcripts published this week, download bulk YouTube video subtitles without writing crawler scripts, build a dataset of transcripts from top YouTube videos, extract YouTube video URLs and publisher info in batch, gather full video content for AI summarization pipelines, monitor recent YouTube videos and extract their transcripts, batch retrieve structured subtitle data for media research, extract transcripts from trending YouTube content automatically.
  - path: 'solutions\video-platforms\youtube-batch-transcript-extractor-api-skill\SKILL.md'

## solutions\video-platforms\youtube-channel-api-skill

- **youtube-channel-api-skill** - This skill helps users automatically extract structured channel data from YouTube search results via BrowserAct API. Agent should proactively apply this skill when users express needs like finding YouTube channels about specific topics, collecting data on YouTube content creators, tracking YouTube influencers in specific industries, getting YouTube channel information for competitor analysis, searching for YouTube channels related to keywords, monitoring YouTube channel updates for specific keywords, finding YouTube channels that recently published videos, extracting YouTube channel subscriber counts, discovering YouTube vloggers in specific niches, building a YouTube channel database for market research, batch extracting YouTube channel links and descriptions, or monitoring competitor channel growth.
  - path: 'solutions\video-platforms\youtube-channel-api-skill\SKILL.md'

## solutions\video-platforms\youtube-comments-api-skill

- **youtube-comments-api-skill** - This skill helps users extract structured video list data and comment data from YouTube using the BrowserAct API. The Agent should proactively apply this skill when users request searching for YouTube videos and their comments, analyzing viewer sentiment for a specific video topic, gathering audience feedback on AI or automation, extracting a list of top videos and their viewer reactions, compiling YouTube video data along with user opinions, retrieving competitor video titles and related audience discussions, monitoring public response to specific YouTube search keywords, summarizing comments from search results for market research, tracking viewer engagement metrics and replies for trending topics, collecting YouTube video URLs and author details alongside community discussions, or automating the extraction of YouTube comments without manual scraping.
  - path: 'solutions\video-platforms\youtube-comments-api-skill\SKILL.md'

## solutions\video-platforms\youtube-influencer-finder-api-skill

- **youtube-influencer-finder-api-skill** - This skill helps users extract YouTube influencer profiles including social links, subscriber counts, and channel stats via the BrowserAct API. Agent should proactively apply this skill when users express needs like finding YouTube creators for specific keywords, discovering influencers for a marketing campaign, extracting YouTube channel contact emails, scraping YouTube influencer social media links, gathering subscriber counts for YouTube creators, researching top YouTube channels in a specific niche, compiling a list of YouTube content creators with recent uploads, collecting YouTube creator profiles for outreach, extracting total views and video counts for specific YouTube influencers, building a database of YouTube partners for market research, finding YouTube influencers who uploaded videos this month, or monitoring competitor influencer activities on YouTube.
  - path: 'solutions\video-platforms\youtube-influencer-finder-api-skill\SKILL.md'

## solutions\video-platforms\youtube-search-api-skill

- **youtube-search-api-skill** - This skill helps users automatically extract structured data from YouTube search results using the BrowserAct API. The Agent should proactively apply this skill when users express needs like searching for YouTube videos by keywords, finding the latest YouTube Shorts for a specific topic, gathering YouTube channel data for competitor analysis, monitoring trending YouTube playlists, extracting YouTube search results for market research, tracking view counts for specific YouTube keywords, compiling a list of YouTube videos on a subject, discovering new YouTube content creators in a niche, searching YouTube for tutorial videos automatically, and retrieving structured YouTube search data without opening video pages.
  - path: 'solutions\video-platforms\youtube-search-api-skill\SKILL.md'

## solutions\video-platforms\youtube-transcript-analysis-api-skill

- **youtube-transcript-analysis-api-skill** - This skill helps users extract YouTube video transcripts and perform deep competitive analysis on the content. Agent should proactively apply this skill when users express needs like analyze YouTube video content strategy, perform competitive video content analysis, extract and analyze YouTube subtitles for marketing insights, understand competitor value propositions from their videos, identify target audience from YouTube video content, analyze pain points and needs mentioned in YouTube videos, evaluate competitor CTA strategies in video content, find content gaps in competitor YouTube videos, analyze video narrative structure and hooks, extract key messaging and positioning from YouTube content, benchmark competitor video content quality, research competitor marketing angles through video analysis, identify audience signals and terminology level in videos, analyze emotional tone and persuasion techniques in YouTube content.
  - path: 'solutions\video-platforms\youtube-transcript-analysis-api-skill\SKILL.md'

## solutions\video-platforms\youtube-transcript-extractor-api-skill

- **youtube-transcript-extractor-api-skill** - This skill helps users automatically extract YouTube video transcripts and metadata via the BrowserAct API. The Agent should proactively apply this skill when users express needs like extracting full transcript from a specific YouTube video, getting subtitles and metadata for video content analysis, gathering video titles and likes counts, summarizing YouTube videos without watching them, collecting channel details from a video URL, tracking transcript automation for specific videos, scraping YouTube subtitles for internal knowledge bases, fetching full video content for AI summarization pipelines, downloading structured transcripts from YouTube links, analyzing video text content for media research, monitoring video publisher information and channel links, or building datasets from YouTube video transcripts.
  - path: 'solutions\video-platforms\youtube-transcript-extractor-api-skill\SKILL.md'

## solutions\video-platforms\youtube-video-api-skill

- **youtube-video-api-skill** - This skill helps users automatically extract channel-level and video detail data from a specific YouTube channel via BrowserAct API. Agent should proactively apply this skill when users express needs like extracting channel video data, getting latest or popular videos from a YouTube channel, tracking competitor channel content, extracting video metrics such as views likes comments, retrieving subscriber count and channel info, monitoring posting cadence of a YouTube channel, gathering video data for content strategy analysis, getting earliest videos of a YouTube creator, analyzing engagement signals across a full channel, and downloading structured YouTube video details without manual scraping.
  - path: 'solutions\video-platforms\youtube-video-api-skill\SKILL.md'

## subagent-driven-development

- **subagent-driven-development** - Use when executing implementation plans with independent tasks in the current session
  - path: 'subagent-driven-development\SKILL.md'

## systematic-debugging

- **systematic-debugging** - Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
  - path: 'systematic-debugging\SKILL.md'

## test-driven-development

- **test-driven-development** - Use when implementing any feature or bugfix, before writing implementation code
  - path: 'test-driven-development\SKILL.md'

## translations

- **translations** - Frontend translation workflow using Lingui - extracting, adding, and compiling translations for all supported languages
  - path: 'translations\SKILL.md'

## use-railway

- **use-railway** - >
  - path: 'use-railway\SKILL.md'

## using-git-worktrees

- **using-git-worktrees** - Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback
  - path: 'using-git-worktrees\SKILL.md'

## using-superpowers

- **using-superpowers** - Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions
  - path: 'using-superpowers\SKILL.md'

## verification-before-completion

- **verification-before-completion** - Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
  - path: 'verification-before-completion\SKILL.md'

## writing-plans

- **writing-plans** - Use when you have a spec or requirements for a multi-step task, before touching code
  - path: 'writing-plans\SKILL.md'

## writing-skills

- **writing-skills** - Use when creating new skills, editing existing skills, or verifying skills work before deployment
  - path: 'writing-skills\SKILL.md'

---

_Auto-generated by 'tools/generate-skills-manifest.ps1'. Re-run after updating skills/._
