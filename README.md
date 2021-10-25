# About

PoetCave is the Django-based recreation of the website [Ljóð.is](https://ljod.is).

In the first phase, we will simply recreate the website's functionality with the intent of getting it functional again. This means that we will begin by imitating arguably bad design decisions made earlier. Such decisions may then be reversed or amended in latter phases.

Features that differ from the original are only different because they must be updated to fit a new paradigm. One example of that is how a poem's status is handled. This is fundamentally different between the old version and the new, so some changes in that area will already be visible to users once Phase 1 is completed.

# Phase 1

*"CRUD" stands for Create/Read/Update/Delete and refers to the ability to apply those operations on the entity in question.*

## Features

### User and profile
- [x] Registration.
- [x] Login/logout.
- [x] Forgotten-password.
- [x] Terms and conditions.
- [x] Personal data download.
- [x] Account deletion.
- [x] Private paths (i.e. https://ljod.is/some-username)

### Poems and authors
- [x] CRUD for poems.
- [X] Poem navigation and search.
- [x] Daily poem displayed on front page.
- [x] Bookmarks
- [x] Poem approval/rejection.
- [x] Send email to author upon editorial decision.

### Critiques
- [ ] CRUD for critiques.
- [ ] Critique approval/rejection.

### News and mailing list
- [ ] CRUD for news (by administrator).
- [ ] Ability to sign-up/sign-off mailing list.
- [ ] Automatic sending of news to mailing list.

### Data import
- [x] Users
- [x] Authors
- [x] Poems
- [x] Daily poems
- [x] Bookmarks
- [x] Private paths
- [ ] News

### Superuser administration
- [x] Poems
- [x] Authors
- [x] Users
- [x] Terms and conditions
- [ ] Day poem selection
- [ ] Critiques

### Other
- [x] Static pages (FAQ, about, etc.)
- [x] List of superusers and moderators.
