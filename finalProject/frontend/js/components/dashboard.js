/**
 * Dashboard Component
 * Main navigation and layout
 */

const dashboardComponent = {
    currentPage: 'profile',
    currentUser: null,

    render() {
        const isAdmin = Boolean(this.currentUser?.is_admin);
        const fullName = [this.currentUser?.first_name, this.currentUser?.last_name].filter(Boolean).join(' ') || this.currentUser?.email || 'Workspace';

        return `
            <div class="app-shell">
                <aside class="sidebar">
                    <div class="brand-mark">
                        <div class="brand-badge">IM</div>
                        <div>
                            <p class="eyebrow">Intern Workspace</p>
                            <h1>Management Portal</h1>
                        </div>
                    </div>

                    <div class="sidebar-section">
                        <p class="sidebar-label">Navigation</p>
                        <div class="nav-stack">
                            ${!isAdmin ? `<button id="navProfile" class="nav-pill">Profile</button>` : ''}
                            <button id="navAssignments" class="nav-pill">Assignments</button>
                            ${isAdmin ? `<button id="navAdmin" class="nav-pill">Admin Review</button>` : ''}
                        </div>
                    </div>

                    <div class="sidebar-card">
                        <p class="sidebar-label">Signed in as</p>
                        <h2>${appUtils.escapeHtml(fullName)}</h2>
                        <p>${appUtils.escapeHtml(this.currentUser?.email || '')}</p>
                        <span class="status-chip ${isAdmin ? 'status-success' : 'status-info'}">${isAdmin ? 'Admin access' : 'Intern access'}</span>
                    </div>

                    <button id="navLogout" class="button button-secondary button-full">Logout</button>
                </aside>

                <main class="content-shell">
                    <section class="hero-panel">
                        <div>
                            <p class="eyebrow">Minimal, focused, polished</p>
                            <h2 id="pageHeading">Welcome back</h2>
                            <p id="pageSubheading" class="hero-copy">Your workspace is ready.</p>
                        </div>
                        <div class="hero-accent"></div>
                    </section>
                    <section id="content" class="content-stack"></section>
                </main>
            </div>
        `;
    },

    async mount() {
        const app = document.getElementById('app');
        this.currentUser = await auth.fetchCurrentUser();

        if (!this.currentUser) {
            auth.logout();
            return;
        }

        if (this.currentUser.is_admin) {
            this.currentPage = 'admin';
        }

        app.innerHTML = this.render();
        this.bindNavigation();
        this.updateNavigationState();
        this.loadPage();
    },

    bindNavigation() {
        document.getElementById('navProfile')?.addEventListener('click', () => {
            this.currentPage = 'profile';
            this.updateNavigationState();
            this.loadPage();
        });

        document.getElementById('navAssignments')?.addEventListener('click', () => {
            this.currentPage = 'assignments';
            this.updateNavigationState();
            this.loadPage();
        });

        document.getElementById('navAdmin')?.addEventListener('click', () => {
            this.currentPage = 'admin';
            this.updateNavigationState();
            this.loadPage();
        });

        document.getElementById('navLogout')?.addEventListener('click', async () => {
            await auth.logout();
        });
    },

    updateNavigationState() {
        document.querySelectorAll('.nav-pill').forEach((button) => {
            button.classList.remove('active');
        });

        const activeMap = {
            profile: 'navProfile',
            assignments: 'navAssignments',
            admin: 'navAdmin'
        };

        document.getElementById(activeMap[this.currentPage])?.classList.add('active');
    },

    updateHero(title, subtitle) {
        const heading = document.getElementById('pageHeading');
        const subheading = document.getElementById('pageSubheading');

        if (heading) heading.textContent = title;
        if (subheading) subheading.textContent = subtitle;
    },

    loadPage() {
        const content = document.getElementById('content');

        switch (this.currentPage) {
            case 'profile':
                this.updateHero('Your profile', 'Keep your internship details fresh and easy to review.');
                profileComponent.mount(content);
                break;
            case 'assignments':
                this.updateHero('Assignments', 'Track tasks, due dates, and submissions in one calm workspace.');
                assignmentsComponent.mount(content);
                break;
            case 'admin':
                this.updateHero('Admin review', 'Create assignments quickly and review submissions without extra clicks.');
                adminComponent.mount(content);
                break;
            default:
                this.currentPage = this.currentUser?.is_admin ? 'admin' : 'profile';
                this.updateNavigationState();
                this.loadPage();
        }
    }
};
