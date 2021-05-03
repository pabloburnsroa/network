document.addEventListener('DOMContentLoaded', function() {


});

function edit(id) {

  document.querySelector(`#edit-text-${id}`).style.display = 'block';
  document.querySelector(`#save-btn-${id}`).style.display = 'block';
  document.querySelector(`#post-${id}`).style.display = 'none';
  document.querySelector(`#edit-${id}`).style.display = 'none';

  document.querySelector(`#save-btn-${id}`).addEventListener('click', () => {
    fetch('/edit/' + id, {
      method: 'PUT',
      body: JSON.stringify({
          post: document.querySelector(`#edit-text-${id}`).value
      })
    })

    document.querySelector(`#edit-text-${id}`).style.display = 'none';
    document.querySelector(`#save-btn-${id}`).style.display = 'none';
    document.querySelector(`#post-${id}`).style.display = 'block';
    document.querySelector(`#edit-${id}`).style.display = 'block';

    document.querySelector(`#post-${id}`).innerHTML = document.querySelector(`#edit-text-${id}`).value

  });
}

function like(id) {
  var like_btn = document.querySelector(`#like-btn-${id}`);
  var like_ct = document.querySelector(`#like-count-${id}`);

    if (like_btn.style.backgroundColor == 'white') {
        fetch('/like/'+`${id}`, {
          method: 'PUT',
          body: JSON.stringify({
            like: true
          })
        })

        like_btn.style.backgroundColor = 'red';
            
        fetch('/like/'+`${id}`)
        .then(response => response.json())
        .then(post => {
          like_ct.innerHTML = post.likes;
        });
    }
    else {
        fetch('/like/'+`${id}`, {
          method: 'PUT',
          body: JSON.stringify({
            like: false
          })
        });
            
        like_btn.style.backgroundColor = 'white';

        fetch('/like/'+`${id}`)
        .then(response => response.json())
        .then(post => {
            like_ct.innerHTML = post.likes;
        });
    }
    return false;
}
