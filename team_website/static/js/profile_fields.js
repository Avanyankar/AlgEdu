document.addEventListener('DOMContentLoaded', function() {
    function loadFields(fieldType) {
        var container = document.getElementById('fields-container');
        container.innerHTML = '<p>Загрузка...</p>';
        
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/api/profile/fields/?type=' + fieldType, true);
        
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                var data = JSON.parse(xhr.responseText);
                renderFields(data.fields);
            } else {
                container.innerHTML = '<p>Ошибка загрузки</p>';
                console.error('Ошибка:', xhr.statusText);
            }
        };
        
        xhr.onerror = function() {
            container.innerHTML = '<p>Ошибка сети</p>';
            console.error('Ошибка сети');
        };
        
        xhr.send();
    }

    function renderFields(fields) {
        var container = document.getElementById('fields-container');
        container.innerHTML = '';
        
        if (fields.length === 0) {
            container.innerHTML = '<p>Нет карт для отображения</p>';
            return;
        }
        
        for (var i = 0; i < fields.length; i++) {
            var field = fields[i];
            var fieldElement = document.createElement('div');
            
            fieldElement.innerHTML = 
                '<h3>' + field.title + '</h3>' +
                '<p>' + (field.description || 'Нет описания') + '</p>' +
                '<small>Создано: ' + field.created_at + '</small>';
            
            fieldElement.onclick = function(id) {
                return function() {
                    window.location.href = '/fields/' + id + '/';
                };
            }(field.id);
            
            container.appendChild(fieldElement);
        }
    }

    var buttons = document.querySelectorAll('.fields-nav-btn');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function() {
            loadFields(this.getAttribute('data-type'));
        });
    }

    if (buttons.length > 0) {
        loadFields('my');
    }
});
