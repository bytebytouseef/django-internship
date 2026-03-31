/**
 * Profile Component
 * Displays and manages intern profile
 */

const profileComponent = {
    async mount(target) {
        try {
            const profile = await api.get('/interns/me/');
            target.innerHTML = this.render(profile);
            this.setupEventListeners();
        } catch (error) {
            target.innerHTML = `
                <section class="panel">
                    <div class="message-banner message-error">
                        ${appUtils.escapeHtml(error.message || 'Unable to load profile.')}
                    </div>
                </section>
            `;
        }
    },

    render(profile) {
        const mentor = profile.assigned_mentor
            ? `${profile.assigned_mentor.first_name} ${profile.assigned_mentor.last_name}`.trim()
            : 'Not assigned';

        return `
            <section class="panel">
                <div class="section-header">
                    <div>
                        <p class="eyebrow">Personal details</p>
                        <h3>My profile</h3>
                    </div>
                    <span class="status-chip status-info">${appUtils.escapeHtml(profile.department || 'Department')}</span>
                </div>

                <form id="profileForm" class="form-stack">
                    <div class="field-grid field-grid-wide">
                        <div class="field">
                            <label for="full_name">Full name</label>
                            <input id="full_name" type="text" name="full_name" value="${appUtils.escapeHtml(profile.full_name)}" class="input-field">
                        </div>
                        <div class="field">
                            <label for="email">Email</label>
                            <input id="email" type="email" name="email" value="${appUtils.escapeHtml(profile.email)}" class="input-field">
                        </div>
                        <div class="field">
                            <label for="department">Department</label>
                            <input id="department" type="text" name="department" value="${appUtils.escapeHtml(profile.department || '')}" class="input-field">
                        </div>
                        <div class="field">
                            <label for="phone">Phone</label>
                            <input id="phone" type="text" name="phone" value="${appUtils.escapeHtml(profile.phone || '')}" class="input-field">
                        </div>
                        <div class="field">
                            <label for="date_of_birth">Date of birth</label>
                            <input id="date_of_birth" type="date" name="date_of_birth" value="${appUtils.escapeHtml(profile.date_of_birth || '')}" class="input-field">
                        </div>
                        <div class="field">
                            <label for="resume_url">Resume URL</label>
                            <input id="resume_url" type="url" name="resume_url" value="${appUtils.escapeHtml(profile.resume_url || '')}" class="input-field">
                        </div>
                        <div class="field">
                            <label for="start_date">Start date</label>
                            <input id="start_date" type="date" name="start_date" value="${appUtils.escapeHtml(profile.start_date || '')}" class="input-field">
                        </div>
                        <div class="field">
                            <label for="end_date">End date</label>
                            <input id="end_date" type="date" name="end_date" value="${appUtils.escapeHtml(profile.end_date || '')}" class="input-field">
                        </div>
                    </div>

                    <div class="field">
                        <label for="skills">Skills</label>
                        <textarea id="skills" name="skills" class="input-field textarea-field" rows="4">${appUtils.escapeHtml(profile.skills || '')}</textarea>
                    </div>

                    <div class="field">
                        <label>Assigned mentor</label>
                        <input type="text" value="${appUtils.escapeHtml(mentor)}" class="input-field" disabled>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="button button-primary">Save changes</button>
                        <div id="profileMessage" class="message-banner message-success hidden">Profile updated successfully.</div>
                    </div>
                </form>
            </section>
        `;
    },

    setupEventListeners() {
        const form = document.getElementById('profileForm');
        form?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            const message = document.getElementById('profileMessage');

            try {
                await api.put('/interns/me_update/', data);
                message.textContent = 'Profile updated successfully.';
                message.className = 'message-banner message-success';
            } catch (error) {
                message.textContent = error.message || 'Unable to update profile.';
                message.className = 'message-banner message-error';
            }
        });
    }
};
