// Ficheiro: static/js/auth_script.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Lógica para Mostrar/Esconder Senha ---
    const passwordFields = document.querySelectorAll('.password-field');
    
    passwordFields.forEach(field => {
        const passwordInput = field.querySelector('input[type="password"]');
        const toggleIcon = field.querySelector('.toggle-password');

        if (toggleIcon) {
            toggleIcon.addEventListener('click', function() {
                // Alterna o tipo do input
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);
                
                // Alterna o ícone
                this.classList.toggle('fa-eye-slash');
            });
        }
    });

    // --- Lógica para o Estado de Carregamento do Botão ---
    const forms = document.querySelectorAll('.form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const button = form.querySelector('.btn');
            if (button) {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Aguarde...';
            }
        });
    });
});
