document.addEventListener("DOMContentLoaded", function () {
    fetch("/user/")
        .then(response => response.json())
        .then(data => {
            document.getElementById("user-img").src = data.images[0]?.url || "";
            document.getElementById("user-btn").onclick = () => {
                const infoBox = document.getElementById("user-info");
                infoBox.innerHTML = `
                    <p><strong>Name:</strong> ${data.display_name}</p>
                    <p><strong>Email:</strong> ${data.email}</p>
                    <p><strong>Country:</strong> ${data.country}</p>
                    <p><strong>Followers:</strong> ${data.followers.total}</p>
                    <p><a href="${data.external_urls.spotify}" target="_blank">Spotify Profile</a></p>
                `;
                infoBox.style.display = infoBox.style.display === "block" ? "none" : "block";
            };
        })
        .catch(error => console.error("Error fetching user data:", error));
});
