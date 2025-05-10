function toggleUserMenu() {
document
  .getElementById('user-menu-dropdown')
  .classList.toggle('hidden');
}
document.addEventListener('click', (e) => {
const btn  = document.getElementById('user-menu-button'),
      menu = document.getElementById('user-menu-dropdown');
if (!btn.contains(e.target) && !menu.contains(e.target)) {
  menu.classList.add('hidden');
}
});

function initiateLogout() {
    const iframe = document.createElement('iframe');
    iframe.style.width = '0px';
    iframe.style.height = '0px';
    iframe.style.border = 'none';
    iframe.src = 'https://accounts.spotify.com/en/logout';
    document.body.appendChild(iframe);

    setTimeout(() => {
        document.body.removeChild(iframe);

        // Call Django logout endpoint via GET
        fetch("/logout/")
        .then(() => {
            window.location.href = '/';
        })
        .catch(error => {
            console.error("Error during logout:", error);
        });

    }, 1500);
}


document.addEventListener("DOMContentLoaded", function () {
    const userPhoto = document.getElementById("user-photo");

    function fetchUserPhoto() {
        fetch("/user/")
            .then(response => response.json())
            .then(data => {
                if (data.images && data.images.length > 0) {
                    userPhoto.src = data.images[0].url;
                }
            })
            .catch(error => {
                console.error("Error fetching user photo:", error);
            });
    }

    fetchUserPhoto();
});
