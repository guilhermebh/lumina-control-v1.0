/**
 * Lumina Control - Business Intelligence Engine
 * Versão: 1.0
 * Descrição: Gerenciamento de estado, lógica de negócio e reatividade do Dashboard.
 */

// 1. Definição do Estado da Aplicação (Store)
// Armazena dados temporários para exibição imediata no Dashboard
const LuminaState = {
    projetos: [
        { id: 1, valor: 4500, custo: 1200, origem: 'Instagram' },
        { id: 2, valor: 7200, custo: 1800, origem: 'Indicação' },
        { id: 3, valor: 3800, custo: 950, origem: 'Google Ads' }
    ],
    config: {
        moeda: 'BRL',
        taxaConversao: 1
    }
};

// 2. Funções de Cálculo (Lógica de Negócio no Frontend)
// Responsável por processar os dados brutos e transformar em métricas de BI
const CalculadoraBI = {
    // Calcula a média de valor de todos os projetos cadastrados
    getTicketMedio: () => {
        const total = LuminaState.projetos.reduce((acc, p) => acc + p.valor, 0);
        return (total / LuminaState.projetos.length) || 0;
    },

    // Calcula o ROI (Retorno sobre Investimento) global da operação
    getROIGlobal: () => {
        const receita = LuminaState.projetos.reduce((acc, p) => acc + p.valor, 0);
        const custos = LuminaState.projetos.reduce((acc, p) => acc + p.custo, 0);
        if (custos === 0) return 0;
        return ((receita - custos) / custos) * 100;
    }
};

// 3. Gerenciamento da Interface (DOM Controller)
// Manipula os elementos HTML para exibir os dados processados
const UIController = {
    // Utilitário para formatar números no padrão de moeda Brasileira
    formatarMoeda: (valor) => {
        return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    },

    // Atualiza os elementos de texto do Dashboard com os valores atuais do estado
    renderizarDashboard: () => {
        const ticketElement = document.getElementById('ticket-medio');
        const roiElement = document.getElementById('roi-total');
        const countElement = document.getElementById('projetos-contagem');

        // Atualização reativa dos cards
        if (ticketElement) ticketElement.textContent = UIController.formatarMoeda(CalculadoraBI.getTicketMedio());
        if (roiElement) roiElement.textContent = `${CalculadoraBI.getROIGlobal().toFixed(1)}%`;
        if (countElement) countElement.textContent = LuminaState.projetos.length;

        console.log("Dashboard Lumina atualizado com sucesso.");
    },

    // Função de Sincronização (Simulação de integração com Backend Python/Flask)
    sincronizarDados: async function() {
        const btn = document.querySelector('.btn-action');
        if (!btn) return;

        // Efeito Visual: Travamento do botão durante o carregamento
        btn.textContent = "Sincronizando...";
        btn.disabled = true;

        // Simulando latência de rede (1.5 segundos)
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Re-processa e renderiza os dados
        this.renderizarDashboard();
        
        btn.textContent = "Sincronizar Dados";
        btn.disabled = false;
        
        // Feedback para o usuário
        alert("Dados do LuminaEngine integrados via SQLite com sucesso!");
    }
};

// 4. Inicialização do Sistema (Ponto de Entrada)
document.addEventListener('DOMContentLoaded', () => {
    // Renderiza o dashboard assim que o documento estiver pronto
    UIController.renderizarDashboard();

    // Configuração de Listeners para interação do usuário
    const btnSync = document.querySelector('.btn-action');
    if (btnSync) {
        btnSync.addEventListener('click', () => {
            UIController.sincronizarDados();
        });
    }
});