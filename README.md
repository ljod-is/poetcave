# About

PoetCave is the Django-based recreation of the website [Ljóð.is](https://ljod.is).

In the first phase, we will simply recreate the website's functionality with the intent of getting it functional again. This means that we will begin by imitating arguably bad design decisions made earlier. Such decisions may then be reversed or amended in latter phases.

# Phase 1

*"CRUD" stands for Create/Read/Update/Delete and refers to the ability to apply those operations on the entity in question.*

## Features

### User and profile
- [x] Registration.
- [x] Login/logout.
- [x] Forgotten-password.
- [ ] Private paths (i.e. https://ljod.is/some-username)
- [ ] Terms and conditions.
- [ ] Personal data download.
- [ ] Account deletion.
- [ ] Combining of accounts sharing an email address.

### Poems and authors
- [x] CRUD for poems.
- [ ] Poems viewable by author.
- [ ] Daily poem displayed on front page.
- [ ] Poem approval/rejection.
- [ ] Bookmarks

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
- [ ] Daily poems
- [ ] Bookmarks
- [ ] News
- [ ] Private paths

### Other
- [ ] Static pages (FAQ, about, etc.)
- [ ] Links

## Decisions

These are decisions that need to be made in order to implement certain functionality.

- [ ] Poem approval process.
- [ ] Critique approval process.
- [ ] What are "links" for and who governs them?
- [ ] Who decides the daily poem?
