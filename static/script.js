document.addEventListener("DOMContentLoaded", function() {
    let input = document.getElementById("liveSearch");
    input.addEventListener('input', async function() {
        const query = input.value;
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });
        const htmlreturn = await response.text();
        document.getElementById("item_container").innerHTML = htmlreturn;
    });
});
