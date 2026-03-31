/**
 * Assignments Component
 * Displays assignments and handles submissions
 */

const assignmentsComponent = {
    async mount(target) {
        try {
            const data = await api.get('/assignments/?limit=100');
            const assignments = data.results || data;
            target.innerHTML = this.render(assignments);
            this.setupEventListeners(target);
        } catch (error) {
            target.innerHTML = `
                <section class="panel">
                    <div class="message-banner message-error">
                        ${appUtils.escapeHtml(error.message || 'Error loading assignments.')}
                    </div>
                </section>
            `;
        }
    },

    render(assignments) {
        const cards = assignments.map((assignment) => `
            <article class="assignment-card">
                <div class="assignment-card-top">
                    <div>
                        <h3>${appUtils.escapeHtml(assignment.title)}</h3>
                        <p>${appUtils.escapeHtml(appUtils.truncate(assignment.description, 130))}</p>
                    </div>
                    <span class="status-chip status-${appUtils.statusTone(assignment.status)}">
                        ${appUtils.escapeHtml(appUtils.statusLabel(assignment.status))}
                    </span>
                </div>
                <div class="assignment-meta">
                    <span>Due ${appUtils.escapeHtml(appUtils.formatDate(assignment.due_date, { month: 'short', day: 'numeric', year: 'numeric' }))}</span>
                    <button class="button button-primary submit-btn" data-id="${assignment.id}" data-title="${appUtils.escapeHtml(assignment.title)}">Submit work</button>
                </div>
            </article>
        `).join('');

        return `
            <section class="panel">
                <div class="section-header">
                    <div>
                        <p class="eyebrow">Tasks overview</p>
                        <h3>My assignments</h3>
                    </div>
                    <div class="compact-stat">
                        <strong>${assignments.length}</strong>
                        <span>Active items</span>
                    </div>
                </div>

                <div class="assignment-grid">
                    ${cards || '<div class="empty-state">No assignments available right now.</div>'}
                </div>
            </section>

            <div id="submitModal" class="modal-shell hidden">
                <div class="modal-backdrop" data-close-modal="true"></div>
                <div class="modal-panel">
                    <div class="section-header">
                        <div>
                            <p class="eyebrow">Submission</p>
                            <h3 id="submitModalTitle">Submit assignment</h3>
                        </div>
                        <button type="button" class="icon-button" data-close-modal="true">Close</button>
                    </div>
                    <form id="submitForm" class="form-stack">
                        <input type="hidden" id="assignmentId" name="assignment_id">
                        <div class="field">
                            <label for="submissionUrl">Submission URL</label>
                            <input type="url" id="submissionUrl" name="submission_url" class="input-field" placeholder="https://example.com/work">
                        </div>
                        <div class="field">
                            <label for="submissionText">Notes</label>
                            <textarea id="submissionText" name="submission_text" class="input-field textarea-field" rows="5" placeholder="Add a short note about what you submitted."></textarea>
                        </div>
                        <div id="submitMessage" class="message-banner hidden"></div>
                        <div class="form-actions">
                            <button type="submit" class="button button-primary">Send submission</button>
                            <button type="button" class="button button-secondary" data-close-modal="true">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },

    setupEventListeners(target) {
        const modal = document.getElementById('submitModal');
        const assignmentIdInput = document.getElementById('assignmentId');
        const modalTitle = document.getElementById('submitModalTitle');
        const submitMessage = document.getElementById('submitMessage');

        document.querySelectorAll('.submit-btn').forEach((button) => {
            button.addEventListener('click', () => {
                assignmentIdInput.value = button.dataset.id;
                modalTitle.textContent = `Submit ${button.dataset.title}`;
                submitMessage.className = 'message-banner hidden';
                submitMessage.textContent = '';
                modal.classList.remove('hidden');
            });
        });

        modal.querySelectorAll('[data-close-modal="true"]').forEach((button) => {
            button.addEventListener('click', () => {
                modal.classList.add('hidden');
            });
        });

        document.getElementById('submitForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();

            try {
                await api.post(`/assignments/${assignmentIdInput.value}/submit/`, {
                    submission_url: document.getElementById('submissionUrl').value,
                    submission_text: document.getElementById('submissionText').value
                });

                modal.classList.add('hidden');
                this.mount(target);
            } catch (error) {
                submitMessage.textContent = error.message || 'Unable to submit assignment.';
                submitMessage.className = 'message-banner message-error';
            }
        });
    }
};
