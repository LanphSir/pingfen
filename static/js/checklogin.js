        // 标签切换逻辑（复用）
        document.querySelectorAll('.tab-btn').forEach(button => {
					button.addEventListener('click', () => {
							const tabId = button.dataset.tab;
							document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
							button.classList.add('active');
							document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
							document.getElementById(tabId).classList.add('active');
					});
			});

			// 登录下拉逻辑（复用）
			const userMenuTrigger = document.getElementById('userMenuTrigger');
			const userDropdown = document.getElementById('userDropdown');
			userMenuTrigger.addEventListener('click', () => userDropdown.classList.toggle('active'));
			document.addEventListener('click', (e) => {
					if (!userMenuTrigger.contains(e.target) && !userDropdown.contains(e.target)) {
							userDropdown.classList.remove('active');
					}
			});

			// 返回主页
			document.querySelector('.go-back-btn')?.addEventListener('click', function() {
					window.location.href = '/'; 
			})

			// 登出
			function logout() {
				document.cookie = "judge_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
				document.cookie = "role=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
				document.cookie = "name=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
				window.location.href = "/login";
			}