function toggleDarkMode() {
            document.documentElement.classList.toggle('dark');
        }

        function toggleFields() {
            const qrType = document.getElementById("qrType").value;
            document.getElementById("urlInput").classList.toggle("hidden", qrType === "vcf");
            document.getElementById("vcfFields").classList.toggle("hidden", qrType !== "vcf");
        }

        function generateQR() {
            let formData = new FormData();
            let qrType = document.getElementById("qrType").value;
            formData.append("qr_type", qrType);
            formData.append("qr_color", document.getElementById("qrColor").value);

            if (qrType === "url") {
                formData.append("data", document.getElementById("qrData").value);
            } else {
                let vcfData = {
                    name: document.getElementById("vcfName").value,
                    phone: document.getElementById("vcfPhone").value,
                    email: document.getElementById("vcfEmail").value,
                    address: document.getElementById("vcfAddress").value
                };
                formData.append("vcf_data", JSON.stringify(vcfData));
            }

            let fileInput = document.getElementById("qrLogo");
            if (fileInput.files.length > 0) {
                formData.append("logo", fileInput.files[0]);
            }

            fetch("/generate", {
                method: "POST",
                body: formData
            })
            .then(response => response.text())
            .then(imageUrl => {
                document.getElementById("qrPreview").src = imageUrl;
                document.getElementById("downloadPng").href = "/download/png";
                document.getElementById("downloadSvg").href = "/download/svg";
            })
            .catch(error => console.error("Error:", error));
        }
        // Dasboard
   function fetchLogs() {
            $.ajax({
                url: "/get_logs",
                type: "GET",
                success: function(response) {
                    let logs = response.logs;
                    let totalVisitors = response.total;

                    let logHtml = "";
                    logs.forEach(log => {
                        logHtml += `<tr class="border-b">
                            <td class="px-4 py-2">${log[0]}</td>
                            <td class="px-4 py-2">${log[1]}</td>
                            <td class="px-4 py-2">${log[2]}</td>
                        </tr>`;
                    });

                    $("#log-table").html(logHtml);
                    $("#total-visitors").text(totalVisitors);
                }
            });
        }

        // Fetch logs on load and update every 10 seconds
        $(document).ready(fetchLogs);
        setInterval(fetchLogs, 10000);

        // Dark/Light Mode Toggle
        const themeToggle = document.getElementById("theme-toggle");
        themeToggle.addEventListener("click", () => {
            document.documentElement.classList.toggle("dark");
        });