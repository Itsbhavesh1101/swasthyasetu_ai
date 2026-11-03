# Patient Indigo Authentication Flow Redesign

## Intent

Replace the green patient palette with the supplied indigo palette and make the public entry flow feel like a conventional, focused authentication experience. A visitor should see only the brand, a login form, and a route to registration; after registration, the existing profile questionnaire continues unchanged.

## Goals

- Use `#12141F`, `#232739`, `#383E5C`, `#4F5580`, `#7B81A8`, `#AFB4CE`, and `#E4E6F0` as the patient design foundation.
- Hide the full patient workspace navigation on `/`, `/login`, and `/register`.
- Present one centered login form on `/` with a clear create-account link.
- Present one centered registration form on `/register`, then continue to `/profile?setup=1` as today.
- Preserve dashboard navigation, patient records, safety affordances, responsiveness, and accessibility.

## Non-goals

- Do not copy the reference image's space illustration or branding.
- Do not change account APIs, session behavior, profile questions, database schema, dependencies, or protected patient features.
- Do not remove the full menu from authenticated product routes.

## Approaches considered

1. Keep the two-form landing page and only hide the menu. This remains visually busy and does not match the requested conventional login flow.
2. Use a login-first landing page with a separate registration screen (chosen). This is familiar, focused, and reuses the existing tested forms and post-registration profile flow.
3. Build a client-side login/register tab switcher. This adds state and complexity without improving the flow over dedicated accessible routes.

## Design

The authentication shell uses a centered luminous panel over a restrained indigo radial-gradient background. It includes the SwasthyaSetu patient brand, one concise heading, one account form, the alternate authentication link, and a small privacy/support footer. It does not render the sidebar, product navigation, workspace header, or feature cards.

The authenticated shell keeps its current responsive sidebar/workspace structure but adopts the new indigo tokens. Safety and urgent-help states remain red so they do not lose meaning. All controls retain visible labels, focus states, contrast, reduced-motion support, and forced-color support.

## Acceptance

- `/`, `/login`, and `/register` render without patient navigation or the patient workspace sidebar.
- `/` contains one sign-in form and a link to `/register`, not an embedded registration form.
- `/register` contains the registration form and retains navigation to `/profile?setup=1` after success.
- Authenticated routes still render the full patient shell and menu.
- The seven supplied palette colors are represented by the patient CSS tokens and meet established contrast targets.
- Frontend tests, lint, type checking, formatting, production builds, and desktop/mobile visual checks pass.
