// Enhanced Authentication JavaScript
document.addEventListener("DOMContentLoaded", function () {
  initializeAuthForms();
  initializePasswordToggle();
  initializeFormValidation();
});

// Initialize authentication forms
function initializeAuthForms() {
  const signupForm = document.getElementById("signupForm");
  if (signupForm) {
    signupForm.addEventListener("submit", handleSignupSubmit);
  }

  const signinForm = document.getElementById("signinForm");
  if (signinForm) {
    signinForm.addEventListener("submit", handleSigninSubmit);
  }

  // Add input animations
  const inputs = document.querySelectorAll(".input-group input");
  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.style.transform = "scale(1.02)";
    });

    input.addEventListener("blur", function () {
      this.parentElement.style.transform = "scale(1)";
    });
  });
}

// Handle signup
async function handleSignupSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const username = form.querySelector("#username")?.value.trim();
  const email = form.querySelector("#email")?.value.trim();
  const password = form.querySelector("#password")?.value;
  const confirmPassword = form.querySelector("#confirmPassword")?.value;
  const termsAccepted = form.querySelector("#terms")?.checked;
  const submitBtn = form.querySelector("#submitBtn");
  const spinner = form.querySelector("#loadingSpinner");
  const btnText = form.querySelector(".btn-text");

  // Validation
  if (!username || !email || !password || !confirmPassword) {
    showToast("Please fill in all required fields", "error");
    return;
  }

  if (username.length < 2) {
    showToast("Username must be at least 2 characters", "error");
    return;
  }

  if (password.length < 6) {
    showToast("Password must be at least 6 characters", "error");
    return;
  }

  if (password !== confirmPassword) {
    showToast("Passwords do not match", "error");
    return;
  }

  if (!termsAccepted) {
    showToast("Please accept the Terms and Privacy Policy", "error");
    return;
  }

  // Loading state
  if (spinner) spinner.classList.remove("hidden");
  if (btnText) btnText.textContent = "Creating Account...";
  if (submitBtn) submitBtn.disabled = true;

  try {
    const res = await fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });

    const data = await res.json();

    if (data.success) {
      showToast("Account created successfully!", "success");
      setTimeout(() => {
        window.location.href = "/signin";
      }, 1500);
    } else {
      showToast(data.message || "Registration failed", "error");
    }
  } catch (err) {
    console.error("Signup error:", err);
    showToast("Network error. Please try again.", "error");
  } finally {
    if (spinner) spinner.classList.add("hidden");
    if (btnText) btnText.textContent = "Create Account";
    if (submitBtn) submitBtn.disabled = false;
  }
}

// Handle signin
async function handleSigninSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const email = form.querySelector("#email")?.value.trim();
  const password = form.querySelector("#password")?.value;
  const submitBtn = form.querySelector("#submitBtn");
  const spinner = form.querySelector("#loadingSpinner");
  const btnText = form.querySelector(".btn-text");

  if (!email || !password) {
    showToast("Email and password are required", "error");
    return;
  }

  if (spinner) spinner.classList.remove("hidden");
  if (btnText) btnText.textContent = "Signing In...";
  if (submitBtn) submitBtn.disabled = true;

  try {
    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (data.success) {
      showToast("Login successful!", "success");
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 800);
    } else {
      showToast(data.message || "Invalid email or password", "error");
    }
  } catch (err) {
    console.error("Signin error:", err);
    showToast("Network error. Please try again.", "error");
  } finally {
    if (spinner) spinner.classList.add("hidden");
    if (btnText) btnText.textContent = "Sign In";
    if (submitBtn) submitBtn.disabled = false;
  }
}

// Password toggle
function initializePasswordToggle() {
  const passwordToggles = document.querySelectorAll(".password-toggle");

  passwordToggles.forEach((toggle) => {
    toggle.addEventListener("click", function () {
      const input = this.previousElementSibling;
      const icon = this.querySelector("i");

      if (input.type === "password") {
        input.type = "text";
        if (icon) {
          icon.classList.remove("fa-eye");
          icon.classList.add("fa-eye-slash");
        }
      } else {
        input.type = "password";
        if (icon) {
          icon.classList.remove("fa-eye-slash");
          icon.classList.add("fa-eye");
        }
      }
    });
  });
}

// Form validation
function initializeFormValidation() {
  const forms = document.querySelectorAll("form");

  forms.forEach((form) => {
    const inputs = form.querySelectorAll("input[required]");

    inputs.forEach((input) => {
      input.addEventListener("blur", validateInput);
      input.addEventListener("input", clearValidationError);
    });
  });
}

function validateInput(e) {
  const input = e.target;
  const value = input.value.trim();
  const type = input.type;
  const name = input.name;

  clearValidationError(e);

  if (!value) {
    showInputError(input, `${getFieldLabel(name)} is required`);
    return false;
  }

  if (type === "email") {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      showInputError(input, "Please enter a valid email address");
      return false;
    }
  }

  if (
    name === "password" &&
    input.form &&
    input.form.querySelector('input[name="confirmPassword"]')
  ) {
    if (value.length < 6) {
      showInputError(input, "Password must be at least 6 characters");
      return false;
    }
  }

  if (name === "confirmPassword") {
    const password = input.form.querySelector('input[name="password"]').value;
    if (value !== password) {
      showInputError(input, "Passwords do not match");
      return false;
    }
  }

  if (name === "username") {
    if (value.length < 2) {
      showInputError(input, "Username must be at least 2 characters");
      return false;
    }
  }

  return true;
}

function showInputError(input, message) {
  const formGroup = input.closest(".form-group");
  const errorElement = formGroup.querySelector(".input-error");

  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = "block";
  }

  input.style.borderColor = "#dc3545";
}

function clearValidationError(e) {
  const input = e.target;
  const formGroup = input.closest(".form-group");
  const errorElement = formGroup.querySelector(".input-error");

  if (errorElement) {
    errorElement.textContent = "";
    errorElement.style.display = "none";
  }

  input.style.borderColor = "#e1e5e9";
}

function getFieldLabel(name) {
  const labels = {
    username: "Username",
    email: "Email",
    password: "Password",
    confirmPassword: "Confirm Password",
  };
  return labels[name] || name;
}

// Toast notifications
function showToast(message, type = "error") {
  // Remove existing toasts
  const existingToasts = document.querySelectorAll(".toast");
  existingToasts.forEach((toast) => toast.remove());

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  const icon = type === "error" ? "fa-exclamation-circle" : "fa-check-circle";

  toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="toast-close">
            <i class="fas fa-times"></i>
        </button>
    `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 5000);
}

// Forgot password
const forgotForm = document.querySelector("#forgotPasswordForm");
if (forgotForm) {
  forgotForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = this.querySelector('input[name="email"]').value.trim();
    const submitBtn = this.querySelector("#submitBtn");
    const btnText = submitBtn.querySelector(".btn-text");
    const spinner = submitBtn.querySelector("#loadingSpinner");

    if (!email) {
      showToast("Email is required", "error");
      return;
    }

    if (spinner) spinner.classList.remove("hidden");
    if (btnText) btnText.textContent = "Sending...";
    submitBtn.disabled = true;

    try {
      const response = await fetch("/reset_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (data.success) {
        showToast(data.message || "Reset instructions sent!", "success");
        this.reset();
        setTimeout(() => {
          window.location.href = "/signin";
        }, 2000);
      } else {
        showToast(data.message || "Failed to send reset email", "error");
      }
    } catch (error) {
      console.error("Forgot password error:", error);
      showToast("Network error. Please try again.", "error");
    } finally {
      if (spinner) spinner.classList.add("hidden");
      if (btnText) btnText.textContent = "Send Reset Instructions";
      submitBtn.disabled = false;
    }
  });
}

// Helper functions for password toggle
function togglePassword() {
  const passwordInput = document.getElementById("password");
  const icon = document.getElementById("passwordIcon");

  if (passwordInput && icon) {
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      icon.classList.remove("fa-eye");
      icon.classList.add("fa-eye-slash");
    } else {
      passwordInput.type = "password";
      icon.classList.remove("fa-eye-slash");
      icon.classList.add("fa-eye");
    }
  }
}

function toggleConfirmPassword() {
  const confirmInput = document.getElementById("confirmPassword");
  const icon = document.getElementById("confirmPasswordIcon");

  if (confirmInput && icon) {
    if (confirmInput.type === "password") {
      confirmInput.type = "text";
      icon.classList.remove("fa-eye");
      icon.classList.add("fa-eye-slash");
    } else {
      confirmInput.type = "password";
      icon.classList.remove("fa-eye-slash");
      icon.classList.add("fa-eye");
    }
  }
}
