document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab') + '-tab';
            document.getElementById(tabId).classList.add('active');
        });
    });

    function loadFields(fieldType) {
        let containerId;
        switch(fieldType) {
            case 'my':
                containerId = 'fields-container';
                break;
            case 'liked':
                containerId = 'liked-fields-container';
                break;
            case 'favorites':
                containerId = 'favorites-fields-container';
                break;
            default:
                return;
        }
        
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '<p>Загрузка...</p>';
        
        fetch(`/api/profile/fields/?type=${fieldType}`)
            .then(response => {
                if (!response.ok) throw new Error('Ошибка загрузки');
                return response.json();
            })
            .then(data => renderFields(container, data.fields))
            .catch(error => {
                console.error('Ошибка:', error);
                container.innerHTML = '<div class="empty-tab-message"><p>Ошибка загрузки данных</p></div>';
            });
    }

    function renderFields(container, fields) {
        container.innerHTML = '';
        
        if (!fields || fields.length === 0) {
            container.innerHTML = '<div class="empty-tab-message"><p>Нет карт для отображения</p></div>';
            return;
        }
        
        fields.forEach(field => {
            const fieldElement = document.createElement('div');
            fieldElement.className = 'field-card';
            fieldElement.innerHTML = `
                <h3>${field.title}</h3>
                <p>${field.description || 'Нет описания'}</p>
                <small>Создано: ${field.created_at}</small>
            `;
            fieldElement.addEventListener('click', () => {
                window.location.href = `/cards/${field.id}/`;
            });
            container.appendChild(fieldElement);
        });
    }

    document.querySelectorAll('.fields-nav-btn').forEach(button => {
        button.addEventListener('click', function() {
            loadFields(this.getAttribute('data-type'));
        });
    });

    if (document.querySelector('.fields-nav-btn.active')) {
        loadFields(document.querySelector('.fields-nav-btn.active').getAttribute('data-type'));
    }
});