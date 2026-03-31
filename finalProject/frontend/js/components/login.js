/**
 * Login Component
 * Handles login and registration forms
 */

const loginComponent = {
    render() {
        return `
            <div class="auth-shell">
                <section class="auth-panel auth-panel-feature">
                    <p class="eyebrow">Intern management</p>
                    <h1>Simple operations, cleaner interface.</h1>
                    <p class="auth-copy">
                        Sign in to manage assignments, track reviews, and keep intern progress organized without clutter.
                    </p>
                    <div class="feature-list">
                        <div class="feature-item">
                            <span class="feature-dot"></span>
                            <span>Minimal dashboard for interns and admins</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-dot"></span>
                            <span>Assignment creation and submission review in one place</span>
                        </div>
                        <div class="feature-item">
                            <span class="feature-dot"></span>
                            <span>Focused UI with low-friction task flow</span>
                        </div>
                    </div>
                </section>

                <section class="auth-panel auth-panel-form">
                    <div class="auth-form-header">
                        <div>
                            <p class="eyebrow">Access portal</p>
                            <h2 id="authTitle">Welcome back</h2>
                        </div>
                        <button id="toggleForm" class="text-button" type="button">Need an account? Create one</button>
                    </div>

                    <form id="loginForm" class="form-stack">
                        <div class="field">
                            <label for="loginEmail">Email</label>
                            <input type="email" id="loginEmail" class="input-field" placeholder="name@example.com" required>
                        </div>
                        <div class="field">
                            <label for="loginPassword">Password</label>
                            <input type="password" id="loginPassword" class="input-field" placeholder="Enter your password" required>
                        </div>
                        <button type="submit" class="button button-primary button-full">Login</button>
                        <div id="loginSuccess" class="message-banner message-success hidden"></div>
                        <div id="loginError" class="message-banner message-error hidden"></div>
                    </form>

                    <form id="registerForm" class="form-stack hidden">
                        <div class="field">
                            <label for="registerEmail">Email</label>
                            <input type="email" id="registerEmail" class="input-field" placeholder="name@example.com" required>
                        </div>
                        <div class="field-grid">
                            <div class="field">
                                <label for="registerUsername">Username</label>
                                <input type="text" id="registerUsername" class="input-field" placeholder="username" required>
                            </div>
                            <div class="field">
                                <label for="registerFirstName">First name</label>
                                <input type="text" id="registerFirstName" class="input-field" placeholder="First name">
                            </div>
                        </div>
                        <div class="field">
                            <label for="registerLastName">Last name</label>
                            <input type="text" id="registerLastName" class="input-field" placeholder="Last name">
                        </div>
                        <div class="field-grid">
                            <div class="field">
                                <label for="registerPassword">Password</label>
                                <input type="password" id="registerPassword" class="input-field" placeholder="Minimum 8 characters" required>
                            </div>
                            <div class="field">
                                <label for="registerPasswordConfirm">Confirm password</label>
                                <input type="password" id="registerPasswordConfirm" class="input-field" placeholder="Repeat password" required>
                            </div>
                        </div>
                        <button type="submit" class="button button-primary button-full">Register</button>
                        <div id="registerError" class="message-banner message-error hidden"></div>
                    </form>
                </section>
            </div>
        `;
    },

    mount() {
        const app = document.getElementById('app');
        app.innerHTML = this.render();

        const toggleForm = document.getElementById('toggleForm');
        const authTitle = document.getElementById('authTitle');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        let isLogin = true;

        toggleForm.addEventListener('click', () => {
            isLogin = !isLogin;
            loginForm.classList.toggle('hidden', !isLogin);
            registerForm.classList.toggle('hidden', isLogin);
            authTitle.textContent = isLogin ? 'Welcome back' : 'Create account';
            toggleForm.textContent = isLogin ? 'Need an account? Create one' : 'Already registered? Login';
        });

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errorDiv = document.getElementById('loginError');
            const successDiv = document.getElementById('loginSuccess');
            errorDiv.classList.add('hidden');
            successDiv.classList.add('hidden');

            const result = await auth.login(
                document.getElementById('loginEmail').value,
                document.getElementById('loginPassword').value
            );

            if (result.success) {
                window.location.hash = '#dashboard';
                return;
            }

            errorDiv.textContent = result.error || 'Login failed. Please try again.';
            errorDiv.classList.remove('hidden');
        });

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errorDiv = document.getElementById('registerError');
            const successDiv = document.getElementById('loginSuccess');
            errorDiv.classList.add('hidden');
            successDiv.classList.add('hidden');

            const result = await auth.register(
                document.getElementById('registerEmail').value,
                document.getElementById('registerUsername').value,
                document.getElementById('registerPassword').value,
                document.getElementById('registerPasswordConfirm').value,
                document.getElementById('registerFirstName').value,
                document.getElementById('registerLastName').value
            );

            if (result.success) {
                isLogin = true;
                loginForm.classList.remove('hidden');
                registerForm.classList.add('hidden');
                authTitle.textContent = 'Welcome back';
                toggleForm.textContent = 'Need an account? Create one';
                registerForm.reset();
                successDiv.textContent = 'Account created successfully. You can log in now.';
                successDiv.classList.remove('hidden');
                return;
            }

            errorDiv.textContent = result.error || 'Registration failed. Please try again.';
            errorDiv.classList.remove('hidden');
        });
    }
};
