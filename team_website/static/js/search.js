document.addEventListener('DOMContentLoaded', function() {
    var searchInput = document.getElementById('search-input');
    var searchButton = document.getElementById('search-button');
    var fieldsList = document.getElementById('fields-list');
    var searchResults = document.getElementById('search-results');
    
    function performSearch() {
        var query = searchInput.value.trim();
        
        if (query.length === 0) {
            resetToDefault();
            return;
        }
        
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/api/search/?q=' + encodeURIComponent(query), true);
        
        xhr.onload = function() {
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    displayResults(data.results);
                } catch (e) {
                    console.error('Ошибка парсинга JSON:', e);
                    searchResults.innerHTML = '<p>Ошибка обработки результатов</p>';
                }
            } else {
                searchResults.innerHTML = '<p>Ошибка сервера</p>';
            }
        };
        
        xhr.onerror = function() {
            searchResults.innerHTML = '<p>Ошибка соединения</p>';
        };
        
        xhr.send();
    }
    
    function displayResults(fields) {
        searchResults.innerHTML = '';
        
        if (fields.length === 0) {
            searchResults.innerHTML = '<p>Ничего не найдено</p>';
            return;
        }
        
        var newList = document.createElement('ul');
        
        for (var i = 0; i < fields.length; i++) {
            var field = fields[i];
            var listItem = document.createElement('li');
            
            listItem.innerHTML = 
                '<h2>' + field.title + '</h2>' +
                '<p>' + (field.description || 'Нет описания') + '</p>' +
                '<p>Создано: ' + field.created_at + '</p>';
            
            listItem.addEventListener('click', (function(id) {
                return function() {
                    window.location.href = '/fields/' + id + '/';
                };
            })(field.id));
            
            newList.appendChild(listItem);
        }
        
        searchResults.appendChild(newList);
    }
    
    function resetToDefault() {
        searchResults.innerHTML = '';
        var originalList = document.createElement('ul');
        originalList.id = 'fields-list';
        originalList.innerHTML = fieldsList.innerHTML;
        searchResults.appendChild(originalList);
    }
    
    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
});