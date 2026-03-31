/**
 * Admin Component
 * Admin dashboard for managing interns and assignments
 */

const adminComponent = {
    currentTab: 'assignments',
    interns: [],
    assignments: [],
    submissions: [],

    async mount(target) {
        target.innerHTML = this.renderShell();
        this.setupTabs();
        await this.loadCurrentTab();
    },

    renderShell() {
        return `
            <section class="panel">
                <div class="section-header">
                    <div>
                        <p class="eyebrow">Admin controls</p>
                        <h3>Assignment and review desk</h3>
                    </div>
                    <div class="tab-row">
                        <button class="tab-button active" data-tab="assignments">Assignments</button>
                        <button class="tab-button" data-tab="submissions">Reviews</button>
                        <button class="tab-button" data-tab="interns">Interns</button>
                    </div>
                </div>
                <div id="adminMessage" class="message-banner hidden"></div>
                <div id="tabContent" class="content-stack"></div>
            </section>
        `;
    },

    setupTabs() {
        document.querySelectorAll('.tab-button').forEach((button) => {
            button.addEventListener('click', async () => {
                this.currentTab = button.dataset.tab;
                document.querySelectorAll('.tab-button').forEach((item) => item.classList.remove('active'));
                button.classList.add('active');
                await this.loadCurrentTab();
            });
        });
    },

    async loadCurrentTab() {
        if (this.currentTab === 'interns') {
            await this.loadInterns();
        } else if (this.currentTab === 'submissions') {
            await this.loadSubmissions();
        } else {
            await this.loadAssignments();
        }
    },

    setMessage(text = '', tone = '') {
        const banner = document.getElementById('adminMessage');
        if (!banner) return;

        if (!text) {
            banner.textContent = '';
            banner.className = 'message-banner hidden';
            return;
        }

        banner.textContent = text;
        banner.className = `message-banner message-${tone || 'success'}`;
    },

    async loadInterns() {
        try {
            const data = await api.get('/interns/?limit=100');
            this.interns = data.results || data;

            const rows = this.interns.map((intern) => `
                <tr>
                    <td>${appUtils.escapeHtml(intern.full_name)}</td>
                    <td>${appUtils.escapeHtml(intern.email)}</td>
                    <td>${appUtils.escapeHtml(intern.department || 'Not set')}</td>
                    <td>${appUtils.escapeHtml(appUtils.formatDate(intern.start_date))}</td>
                    <td>${appUtils.escapeHtml(appUtils.formatDate(intern.end_date))}</td>
                </tr>
            `).join('');

            document.getElementById('tabContent').innerHTML = `
                <div class="table-card">
                    <div class="section-header">
                        <div>
                            <p class="eyebrow">People</p>
                            <h3>Current interns</h3>
                        </div>
                        <div class="compact-stat">
                            <strong>${this.interns.length}</strong>
                            <span>Profiles</span>
                        </div>
                    </div>
                    <div class="table-container">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Department</th>
                                    <th>Start</th>
                                    <th>End</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows || '<tr><td colspan="5" class="empty-row">No interns found.</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            this.renderError(error);
        }
    },

    async loadAssignments() {
        try {
            const [assignmentData, internData] = await Promise.all([
                api.get('/assignments/?limit=100'),
                api.get('/interns/?limit=100')
            ]);

            this.assignments = assignmentData.results || assignmentData;
            this.interns = internData.results || internData;

            const assignmentRows = this.assignments.map((assignment) => `
                <tr>
                    <td>${appUtils.escapeHtml(assignment.title)}</td>
                    <td>${appUtils.escapeHtml(assignment.assigned_to_name || 'Unassigned')}</td>
                    <td>${appUtils.escapeHtml(appUtils.formatDate(assignment.due_date))}</td>
                    <td>
                        <span class="status-chip status-${appUtils.statusTone(assignment.status)}">
                            ${appUtils.escapeHtml(appUtils.statusLabel(assignment.status))}
                        </span>
                    </td>
                </tr>
            `).join('');

            const internOptions = this.interns.map((intern) => `
                <option value="${intern.id}">${appUtils.escapeHtml(intern.full_name)} (${appUtils.escapeHtml(intern.department || 'No department')})</option>
            `).join('');

            document.getElementById('tabContent').innerHTML = `
                <div class="admin-grid">
                    <div class="panel panel-muted">
                        <div class="section-header">
                            <div>
                                <p class="eyebrow">Create</p>
                                <h3>New assignment</h3>
                            </div>
                        </div>
                        <form id="assignmentForm" class="form-stack">
                            <div class="field">
                                <label for="assignmentTitle">Title</label>
                                <input id="assignmentTitle" name="title" class="input-field" placeholder="Frontend polish task" required>
                            </div>
                            <div class="field">
                                <label for="assignmentDescription">Description</label>
                                <textarea id="assignmentDescription" name="description" class="input-field textarea-field" rows="5" placeholder="Describe the task and expected outcome." required></textarea>
                            </div>
                            <div class="field">
                                <label for="assignmentIntern">Assign to</label>
                                <select id="assignmentIntern" name="assigned_to" class="input-field" required>
                                    <option value="">Select an intern</option>
                                    ${internOptions}
                                </select>
                            </div>
                            <div class="field">
                                <label for="assignmentDueDate">Due date</label>
                                <input id="assignmentDueDate" name="due_date" type="datetime-local" class="input-field" required>
                            </div>
                            <div id="assignmentFormMessage" class="message-banner hidden"></div>
                            <button type="submit" class="button button-primary">Create assignment</button>
                        </form>
                    </div>

                    <div class="table-card">
                        <div class="section-header">
                            <div>
                                <p class="eyebrow">Overview</p>
                                <h3>Recent assignments</h3>
                            </div>
                            <div class="compact-stat">
                                <strong>${this.assignments.length}</strong>
                                <span>Total</span>
                            </div>
                        </div>
                        <div class="table-container">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Title</th>
                                        <th>Assigned to</th>
                                        <th>Due date</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${assignmentRows || '<tr><td colspan="4" class="empty-row">No assignments created yet.</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

            this.setupAssignmentForm();
        } catch (error) {
            this.renderError(error);
        }
    },

    setupAssignmentForm() {
        const form = document.getElementById('assignmentForm');
        const message = document.getElementById('assignmentFormMessage');

        form?.addEventListener('submit', async (e) => {
            e.preventDefault();
            message.className = 'message-banner hidden';
            message.textContent = '';

            const dueDateValue = document.getElementById('assignmentDueDate').value;
            const payload = {
                title: document.getElementById('assignmentTitle').value,
                description: document.getElementById('assignmentDescription').value,
                assigned_to: Number(document.getElementById('assignmentIntern').value),
                due_date: new Date(dueDateValue).toISOString()
            };

            try {
                await api.post('/assignments/', payload);
                this.setMessage('Assignment created successfully.', 'success');
                await this.loadAssignments();
            } catch (error) {
                message.textContent = error.message || 'Unable to create assignment.';
                message.className = 'message-banner message-error';
            }
        });
    },

    async loadSubmissions() {
        try {
            const data = await api.get('/assignments/submissions/?limit=100');
            this.submissions = data.results || data;

            const cards = this.submissions.map((submission) => `
                <article class="review-card">
                    <div class="review-card-top">
                        <div>
                            <p class="eyebrow">Submission</p>
                            <h3>${appUtils.escapeHtml(submission.assignment_title)}</h3>
                            <p>${appUtils.escapeHtml(submission.submitted_by_name || 'Unknown intern')}</p>
                        </div>
                        <span class="status-chip status-${appUtils.statusTone(submission.status)}">
                            ${appUtils.escapeHtml(appUtils.statusLabel(submission.status))}
                        </span>
                    </div>
                    <div class="review-body">
                        <p><strong>Submitted:</strong> ${appUtils.escapeHtml(appUtils.formatDateTime(submission.submitted_at))}</p>
                        <p><strong>Link:</strong> ${submission.submission_url ? `<a href="${appUtils.escapeHtml(submission.submission_url)}" target="_blank" rel="noopener noreferrer">Open submission</a>` : 'No URL provided'}</p>
                        <p>${appUtils.escapeHtml(submission.submission_text || 'No notes attached.')}</p>
                    </div>
                    <form class="review-form" data-id="${submission.id}">
                        <label for="feedback-${submission.id}">Feedback</label>
                        <textarea id="feedback-${submission.id}" class="input-field textarea-field" rows="3" placeholder="Add review notes">${appUtils.escapeHtml(submission.reviewer_feedback || '')}</textarea>
                        <div class="review-actions">
                            <button type="button" class="button button-primary review-action" data-action="approve" data-id="${submission.id}">Approve</button>
                            <button type="button" class="button button-secondary review-action" data-action="reject" data-id="${submission.id}">Reject</button>
                        </div>
                    </form>
                </article>
            `).join('');

            document.getElementById('tabContent').innerHTML = `
                <div class="review-grid">
                    ${cards || '<div class="empty-state">No submissions available to review right now.</div>'}
                </div>
            `;

            this.setupReviewActions();
        } catch (error) {
            this.renderError(error);
        }
    },

    setupReviewActions() {
        document.querySelectorAll('.review-action').forEach((button) => {
            button.addEventListener('click', async () => {
                const submissionId = button.dataset.id;
                const action = button.dataset.action;
                const feedback = document.getElementById(`feedback-${submissionId}`)?.value || '';

                try {
                    await api.post(`/assignments/submissions/${submissionId}/${action}/`, { feedback });
                    this.setMessage(
                        action === 'approve' ? 'Submission approved.' : 'Submission sent back for revision.',
                        action === 'approve' ? 'success' : 'warning'
                    );
                    await this.loadSubmissions();
                } catch (error) {
                    this.setMessage(error.message || 'Unable to update submission.', 'error');
                }
            });
        });
    },

    renderError(error) {
        document.getElementById('tabContent').innerHTML = `
            <div class="message-banner message-error">
                ${appUtils.escapeHtml(error.message || 'Something went wrong.')}
            </div>
        `;
    }
};
