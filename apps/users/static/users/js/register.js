document.getElementById('registrationForm').addEventListener('submit', function(e) {
  var role = this.querySelector('select[name="role"]').value;
  var companyId = this.querySelector('input[name="company_id"]').value.trim();
  if (role === 'CompanyAdmin' && !companyId) {
    alert('Company ID is required for CompanyAdmin role.');
    e.preventDefault();
  }
});
