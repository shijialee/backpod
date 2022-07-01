"use strict";

window.onload = function() {
  let feedUrlButton = document.getElementById('feedUrlButton');
  feedUrlButton?.addEventListener('click', function (e) {
    let urlInput = document.getElementById('feedUrl');
    let data = { 'url': urlInput.value };

    fetch('https://backpod-web-5nkbg7zlqa-uw.a.run.app/feeds', {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
	.then(r => {
	  if (!r.ok) {
        if (r.headers.get('content-type')?.includes('application/json')) {
		  r.json().then(data => {throw new Error(data.message)});
		}
		throw new Error('failed to request content');
	  }
	  return r.json();
	})
	.then(data => {
      location = '/feed.html?id=' + data.id
	})
	.catch(error => {
      alert(error.message ?? "failed to request content");
	});
  });
};
