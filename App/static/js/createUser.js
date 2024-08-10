document.getElementById('userForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const jsonData = {};
    formData.forEach((value, key) => { jsonData[key] = value });

    var createUserUrl = urls.createUserUrl;
    var homeUrl = urls.homeUrl;

    fetch(createUserUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Custom-Header': 'Fetch',
            'X-CSRFToken': csrfToken, // Token CSRF
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            window.location.href = homeUrl;
        } else if (data.errors) {
            let errors = data.errors;
            for (let field in errors) {
                alert(`${field}: ${errors[field].join(', ')}`);
            }
        }
    })
    .catch(error => {
        console.log('Error:', error);
        alert('Error desconocido');
    });
});
