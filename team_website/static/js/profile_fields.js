document.addEventListener('DOMContentLoaded', function() {
    function activateButton(button) {
        document.querySelectorAll('.fields-nav-btn').forEach(btn => {
            btn.style.background = '#f0f0f0';
            btn.style.color = '#000';
        });
        
        button.style.background = '#4CAF50';
        button.style.color = 'white';
    }

    function loadFields(fieldType) {
        const container = document.getElementById('fields-container');
        container.innerHTML = '<p style="grid-column: 1 / -1; text-align: center;">Загрузка...</p>';
        
        fetch(`/api/profile/fields/?type=${fieldType}`)
            .then(response => {
                if (!response.ok) throw new Error('Ошибка загрузки');
                return response.json();
            })
            .then(data => {
                renderFields(data.fields);
            })
            .catch(error => {
                container.innerHTML = `<p style="grid-column: 1 / -1; text-align: center; color: red;">${error.message}</p>`;
                console.error('Ошибка:', error);
            });
    }

    function renderFields(fields) {
        const container = document.getElementById('fields-container');
        container.innerHTML = '';
        
        if (fields.length === 0) {
            container.innerHTML = '<p style="grid-column: 1 / -1; text-align: center;">Нет карт для отображения</p>';
            return;
        }
        
        fields.forEach(field => {
            const fieldElement = document.createElement('div');
            fieldElement.style.border = '1px solid #ddd';
            fieldElement.style.borderRadius = '5px';
            fieldElement.style.padding = '10px';
            fieldElement.style.cursor = 'pointer';
            fieldElement.style.transition = 'box-shadow 0.3s';
            
            fieldElement.onmouseover = () => {
                fieldElement.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
            };
            
            fieldElement.onmouseout = () => {
                fieldElement.style.boxShadow = 'none';
            };
            
            fieldElement.onclick = () => {
                window.location.href = `/fields/${field.id}/`;
            };
            
            fieldElement.innerHTML = `
                <h3 style="margin-top: 0; margin-bottom: 10px;">${field.title}</h3>
                <p style="margin: 0; color: #555; font-size: 0.9em;">${field.description || 'Нет описания'}</p>
                <p style="margin: 5px 0 0 0; font-size: 0.8em; color: #888;">
                    Создано: ${field.created_at}
                </p>
            `;
            
            container.appendChild(fieldElement);
        });
    }

    const buttons = document.querySelectorAll('.fields-nav-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            activateButton(this);
            loadFields(this.dataset.type);
        });
    });

    if (buttons.length > 0) {
        buttons[0].click();
    }
});
