// Validates the form on submit: requires company_id if role is CompanyAdmin
document.getElementById('registrationForm').addEventListener('submit', function(e) {
  const role = this.querySelector('select[name="role"]').value;
  const companyIdInput = this.querySelector('input[name="company_id"]');
  const companyId = companyIdInput?.value.trim();

  if (role === 'CompanyAdmin' && !companyId) {
    alert('Company ID is required for CompanyAdmin role.');
    e.preventDefault();
    companyIdInput?.focus();
  }
});

// Runs after the page is loaded: toggles company_id visibility based on role
document.addEventListener('DOMContentLoaded', function() {
  const roleField = document.querySelector('select[name="role"]');
  const companyField = document.querySelector('input[name="company_id"]')?.closest('p');

  if (roleField && companyField) {
    function toggleCompanyField() {
      companyField.style.display = roleField.value === 'CompanyAdmin' ? '' : 'none';
    }

    roleField.addEventListener('change', toggleCompanyField);
    toggleCompanyField();
  }

  // Removes flash messages from the UI after 5 seconds
  setTimeout(() => {
    document.querySelectorAll('.messages li').forEach(el => el.remove());
  }, 5000);
});
