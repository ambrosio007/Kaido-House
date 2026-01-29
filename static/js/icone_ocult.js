document.addEventListener('DOMContentLoaded', async () => {
            // 1. Recupera o token salvo no Login
            const token = localStorage.getItem('token');
            
            // Elementos da DOM
            const loginIcon = document.getElementById('profile-target');
            const profileIcon = document.getElementById('profile-target-logged');
            const cartBadge = document.querySelector('.cart-badge');

            // 2. Controle de Exibição (Login vs Perfil)
            if (token) {
                // Usuário Logado
                if(loginIcon) loginIcon.classList.add('hidden');
                if(profileIcon) profileIcon.classList.remove('hidden');
                
                // Opcional: Atualizar nome ou foto se tiver salvo no localStorage
                // const userName = localStorage.getItem('user_name');
                // console.log("Bem-vindo de volta, " + userName);
            } else {
                // Visitante
                if(loginIcon) loginIcon.classList.remove('hidden');
                if(profileIcon) profileIcon.classList.add('hidden');
            }

            // 3. Atualizar Contador do Carrinho (Consumindo a API)
            try {
                // Prepara os headers (se tiver token, envia; se não, vai sem token)
                const headers = {
                    'Content-Type': 'application/json'
                };
                
                if (token) {
                    headers['Authorization'] = 'Bearer ' + token;
                }

                // Chama a rota que criamos no carrinho_controller.py
                const response = await fetch('/api/carrinho/total', {
                    method: 'GET',
                    headers: headers
                });

                if (response.ok) {
                    const data = await response.json();
                    // Atualiza o número no ícone do carrinho
                    if (cartBadge) {
                        cartBadge.innerText = data.total_itens || 0;
                        
                        // Se quiser esconder o badge quando for zero:
                        if (data.total_itens === 0) {
                            cartBadge.style.display = 'none';
                        } else {
                            cartBadge.style.display = 'flex'; // ou block
                        }
                    }
                }
            } catch (error) {
                console.error("Erro ao atualizar carrinho:", error);
            }
        });