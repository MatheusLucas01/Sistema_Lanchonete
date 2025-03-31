from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QMessageBox, QInputDialog, QSpacerItem,
                             QSizePolicy, QFrame, QScrollArea, QTabWidget, QGridLayout,
                             QSpinBox, QListWidget, QListWidgetItem, QDoubleSpinBox,
                             QDateEdit, QFileDialog, QDialog, QDialogButtonBox, QHeaderView) # Adicionado QDateEdit
from PyQt6.QtCore import Qt, QDateTime, QSize, QDate, QTime, QPropertyAnimation, QVariantAnimation# Adicionado QDate
from PyQt6.QtGui import QIcon, QFont, QDoubleValidator, QPixmap, QColor
import json
import os
from datetime import datetime, timedelta # Para cálculos de data nos relatórios
import pandas as pd
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGridLayout, QFrame, QSpacerItem, QSizePolicy) # Widgets necessários
from PyQt6.QtCore import Qt, QDateTime, QDate, QTime
from PyQt6.QtGui import QFont
import json
import os
from collections import defaultdict # Para contar pagamentos e agrupar por dia
import pyqtgraph as pg # Biblioteca de gráficos

# --- Classe Dashboard (SIMPLIFICADA + GRÁFICOS) ---
class Dashboard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        print("--- Dashboard c/ Gráficos: __init__ chamado ---")
        self.main_window = main_window
        self.setStyleSheet("background-color: #3cb371;") # Fundo verde, Titulo do dashboard
        self.setMinimumSize(800, 600) # Tamanho mínimo da janela

        # Configuração global do pyqtgraph (fundo branco, eixos pretos)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # --- Layout Principal ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(20)

        # --- Título ---
        title_label = QLabel(f"Resumo e Desempenho - {QDate.currentDate().toString('dd/MM/yyyy')}")
        title_font = QFont(); title_font.setPointSize(18); title_font.setBold(True)
        title_label.setFont(title_font); title_label.setStyleSheet("color: #343a40; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label)

        # --- Frame para os Indicadores ---
        metrics_frame = QFrame(); metrics_frame.setFrameShape(QFrame.Shape.StyledPanel)
        metrics_frame.setStyleSheet("QFrame { background-color: #f8f9fa; border-radius: 8px; }")
        metrics_layout = QGridLayout(metrics_frame)
        metrics_layout.setContentsMargins(20, 20, 20, 20); metrics_layout.setSpacing(15)
        self.main_layout.addWidget(metrics_frame)

        # Labels de Título e Valor (como antes)
        label_font = QFont(); label_font.setPointSize(12)
        value_font = QFont(); value_font.setPointSize(16); value_font.setBold(True)
        # ... (Criação das labels total_sales_title, sales_count_title, avg_ticket_title)
        total_sales_title = QLabel("Total de Vendas Hoje:"); total_sales_title.setFont(label_font)
        sales_count_title = QLabel("Número de Vendas Hoje:"); sales_count_title.setFont(label_font)
        avg_ticket_title = QLabel("Ticket Médio Hoje:"); avg_ticket_title.setFont(label_font)
        # ... (Criação das labels self.total_sales_value, self.sales_count_value, self.avg_ticket_value)
        self.total_sales_value = QLabel("R$ 0.00"); self.total_sales_value.setFont(value_font); self.total_sales_value.setStyleSheet("color: #28a745;")
        self.sales_count_value = QLabel("0"); self.sales_count_value.setFont(value_font); self.sales_count_value.setStyleSheet("color: #17a2b8;")
        self.avg_ticket_value = QLabel("R$ 0.00"); self.avg_ticket_value.setFont(value_font); self.avg_ticket_value.setStyleSheet("color: #ffc107;")

        # Adicionando ao Grid Layout (como antes)
        metrics_layout.addWidget(total_sales_title, 0, 0); metrics_layout.addWidget(self.total_sales_value, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        metrics_layout.addWidget(sales_count_title, 1, 0); metrics_layout.addWidget(self.sales_count_value, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        metrics_layout.addWidget(avg_ticket_title, 2, 0); metrics_layout.addWidget(self.avg_ticket_value, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)

        # --- Layout para os Gráficos ---
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        self.main_layout.addLayout(charts_layout, 1) # O '1' faz os gráficos expandirem

        # --- Gráfico 1: Vendas por Método de Pagamento (Hoje) ---
        self.payment_chart_widget = pg.PlotWidget()
        self.payment_chart_widget.setTitle("Vendas por Pagamento (Hoje)", color='k', size='12pt')
        self.payment_chart_widget.setLabel('left', 'Nº de Vendas', color='k')
        self.payment_chart_widget.setLabel('bottom', 'Método', color='k')
        self.payment_chart_widget.showGrid(x=False, y=True, alpha=0.3)
        self.payment_chart_widget.getAxis('bottom').setTextPen('k') # Cor do texto do eixo
        self.payment_chart_widget.getAxis('left').setTextPen('k')
        self.payment_chart_widget.getViewBox().setBackgroundColor("#ffffff00") # Fundo transparente para o viewbox
        charts_layout.addWidget(self.payment_chart_widget)

        # --- Gráfico 2: Total de Vendas por Dia (Últimos 7 Dias) ---
        self.revenue_chart_widget = pg.PlotWidget()
        self.revenue_chart_widget.setTitle("Vendas por Dia (Últimos 7 Dias)", color='k', size='12pt')
        self.revenue_chart_widget.setLabel('left', 'Total (R$)', color='k')
        self.revenue_chart_widget.setLabel('bottom', 'Data', color='k')
        self.revenue_chart_widget.showGrid(x=False, y=True, alpha=0.3)
        self.revenue_chart_widget.getAxis('bottom').setTextPen('k')
        self.revenue_chart_widget.getAxis('left').setTextPen('k')
        self.revenue_chart_widget.getViewBox().setBackgroundColor("#ffffff00")
        charts_layout.addWidget(self.revenue_chart_widget)
        # self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))

        print("--- Dashboard c/ Gráficos: __init__ concluído ---")


    # --- Método de Atualização (MODIFICADO PARA INCLUIR DADOS DOS GRÁFICOS) ---
    def update_summary(self):
        """Lê vendas.json e atualiza os indicadores e gráficos."""
        print("--- Dashboard c/ Gráficos: Iniciando update_summary ---")
        today_qdate = QDate.currentDate()
        today_str_iso = today_qdate.toString(Qt.DateFormat.ISODate)
        print(f"--- Dashboard: Data de hoje para comparação: {today_str_iso}")

        total_sales_today = 0.0
        sales_count_today = 0
        payment_counts = defaultdict(int) # Para contar métodos de pagamento de hoje
        daily_revenue = defaultdict(float) # Para somar vendas dos últimos 7 dias

        # Calcula o intervalo dos últimos 7 dias (incluindo hoje)
        start_date_7_days = today_qdate.addDays(-6)
        date_range_str = [start_date_7_days.addDays(i).toString(Qt.DateFormat.ISODate) for i in range(7)]
        # Inicializa o dicionário de receita com 0 para todos os dias do intervalo
        for date_str in date_range_str:
            daily_revenue[date_str] = 0.0

        print(f"--- Dashboard: Intervalo para gráfico de receita: {start_date_7_days.toString(Qt.DateFormat.ISODate)} a {today_str_iso}")

        sales_data = []
        # Valores padrão para labels
        display_total = "R$ 0.00"; display_count = "0"; display_avg_ticket = "R$ 0.00"

        try:
            sales_file_path = self.main_window.SALES_FILE
            print(f"--- Dashboard: Tentando ler o arquivo: {sales_file_path}")
            if os.path.exists(sales_file_path):
                with open(sales_file_path, "r", encoding='utf-8') as f:
                    sales_data = json.load(f)
                print(f"--- Dashboard: Arquivo lido. {len(sales_data)} registros encontrados.")

                # Processa os dados lidos
                for index, sale in enumerate(sales_data):
                    try: # Try interno para cada registro
                        if 'data' not in sale: continue
                        sale_dt_str = sale['data']
                        current_sale_total = sale.get('total', 0.0)
                        payment_method = sale.get('metodo_pagamento', 'N/A') # Pega o método

                        if not isinstance(current_sale_total, (int, float)): current_sale_total = 0.0

                        sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODate)
                        if not sale_dt.isValid(): sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODateWithMs)

                        if sale_dt.isValid():
                            sale_date_str_iso = sale_dt.date().toString(Qt.DateFormat.ISODate)

                            # Processa para indicadores e gráfico de pagamento (HOJE)
                            if sale_date_str_iso == today_str_iso:
                                total_sales_today += current_sale_total
                                sales_count_today += 1
                                payment_counts[payment_method] += 1

                            # Processa para gráfico de receita (ÚLTIMOS 7 DIAS)
                            if sale_date_str_iso in daily_revenue:
                                daily_revenue[sale_date_str_iso] += current_sale_total

                    except Exception as e_inner:
                        print(f"--- ERRO (Registro {index}): Erro ao processar venda individual: {e_inner} - Registro: {sale}")

                print("--- Dashboard: Iteração concluída.")

                # Calcula labels
                display_total = f"R$ {total_sales_today:.2f}"
                display_count = str(sales_count_today)
                if sales_count_today > 0:
                    avg_ticket = total_sales_today / sales_count_today
                    display_avg_ticket = f"R$ {avg_ticket:.2f}"
                else:
                    display_avg_ticket = "R$ 0.00"

            else:
                print(f"--- Dashboard: Arquivo {sales_file_path} não encontrado.")

        except json.JSONDecodeError as e:
            print(f"--- ERRO CRÍTICO: Falha ao decodificar JSON: {e}")
            QMessageBox.critical(self, "Erro de Arquivo", f"O arquivo de vendas ({os.path.basename(sales_file_path)}) parece corrompido.")
        except Exception as e_outer:
            print(f"--- ERRO INESPERADO em update_summary: {e_outer}")

        # --- Atualização Final das Labels ---
        print(f"--- Dashboard: Atualizando labels. Total: {display_total}, Contagem: {display_count}, Ticket Médio: {display_avg_ticket}")
        self.total_sales_value.setText(display_total)
        self.sales_count_value.setText(display_count)
        self.avg_ticket_value.setText(display_avg_ticket)

        # --- Atualização dos Gráficos ---
        print(f"--- Dashboard: Atualizando gráfico de pagamentos. Dados: {dict(payment_counts)}")
        self.update_payment_chart(payment_counts)

        print(f"--- Dashboard: Atualizando gráfico de receita diária. Dados: {dict(daily_revenue)}")
        self.update_revenue_chart(daily_revenue)

        print("--- Dashboard c/ Gráficos: update_summary concluído ---")

    # --- FUNÇÃO PARA ATUALIZAR GRÁFICO DE PAGAMENTOS ---
    def update_payment_chart(self, payment_data):
        self.payment_chart_widget.clear() # Limpa o gráfico anterior

        if not payment_data:
            # Opcional: Mostrar texto se não houver dados
            text = pg.TextItem("Sem dados de pagamento hoje", color='gray', anchor=(0.5, 0.5))
            self.payment_chart_widget.addItem(text)
            # Redefinir eixos se necessário para limpar ticks antigos
            self.payment_chart_widget.getAxis('bottom').setTicks(None)
            self.payment_chart_widget.getAxis('left').setTicks(None)
            return # Sai se não houver dados

        # Prepara dados para o gráfico de barras
        methods = list(payment_data.keys())
        counts = list(payment_data.values())
        x_values = list(range(len(methods))) # Posições numéricas para as barras

        # Cria o item de gráfico de barras
        bars = pg.BarGraphItem(x=x_values, height=counts, width=0.6, brush='b') # 'b' = blue brush
        self.payment_chart_widget.addItem(bars)

        # Configura os ticks do eixo X para mostrar os nomes dos métodos
        ticks = [(i, methods[i]) for i in x_values]
        axis_bottom = self.payment_chart_widget.getAxis('bottom')
        axis_bottom.setTicks([ticks])
        axis_bottom.setStyle(tickTextOffset=10) # Ajusta o espaçamento do texto
        axis_bottom.setTickFont(QFont("Arial", 10)) # Define a fonte dos ticks

        # Ajusta o range do eixo Y (opcional, para dar espaço acima das barras)
        max_count = max(counts) if counts else 1
        self.payment_chart_widget.setYRange(0, max_count * 1.1)
        # Remove o range do eixo X para auto-ajuste
        self.payment_chart_widget.setXRange(-0.5, len(methods) - 0.5) # Ajusta para centralizar barras

    # --- FUNÇÃO PARA ATUALIZAR GRÁFICO DE RECEITA DIÁRIA ---
    def update_revenue_chart(self, revenue_data):
        self.revenue_chart_widget.clear() # Limpa o gráfico anterior

        if not revenue_data or all(v == 0 for v in revenue_data.values()):
             # Opcional: Mostrar texto se não houver dados
            text = pg.TextItem("Sem dados de receita no período", color='gray', anchor=(0.5, 0.5))
            self.revenue_chart_widget.addItem(text)
             # Redefinir eixos se necessário para limpar ticks antigos
            self.revenue_chart_widget.getAxis('bottom').setTicks(None)
            self.revenue_chart_widget.getAxis('left').setTicks(None)
            return # Sai se não houver dados

        # Ordena os dados por data (chave do dicionário)
        sorted_dates = sorted(revenue_data.keys())
        totals = [revenue_data[date_str] for date_str in sorted_dates]
        x_values = list(range(len(sorted_dates))) # Posições numéricas

        # Cria o item de gráfico de barras
        bars = pg.BarGraphItem(x=x_values, height=totals, width=0.6, brush='g') # 'g' = green brush
        self.revenue_chart_widget.addItem(bars)

        # Configura os ticks do eixo X para mostrar as datas formatadas (dd/MM)
        ticks = []
        for i, date_str_iso in enumerate(sorted_dates):
            qdate = QDate.fromString(date_str_iso, Qt.DateFormat.ISODate)
            if qdate.isValid():
                ticks.append((i, qdate.toString("dd/MM"))) # Formato curto
            else:
                ticks.append((i, "Inválida")) # Fallback

        axis_bottom = self.revenue_chart_widget.getAxis('bottom')
        axis_bottom.setTicks([ticks])
        axis_bottom.setStyle(tickTextOffset=10)
        axis_bottom.setTickFont(QFont("Arial", 10))

        # Ajusta o range do eixo Y
        max_revenue = max(totals) if totals else 1
        self.revenue_chart_widget.setYRange(0, max_revenue * 1.1)
        # Remove o range do eixo X para auto-ajuste
        self.revenue_chart_widget.setXRange(-0.5, len(sorted_dates) - 0.5)



# --- Classes das Abas (Cadastro, Estoque, Vendas(Gerente), Fiscal, Config - Inalteradas) ---
class CadastroTab(QWidget):
    # --- Cadastro de Produtos (SIMPLIFICADO) ---
    def __init__(self, main_window): # Recebe a instância principal
        super().__init__()
        self.main_window = main_window
        self.selected_product_id = None # Rastreia o ID do produto selecionado para edição
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(10)
        form_layout.addWidget(QLabel("Nome:*"), 0, 0)
        self.name_input = QLineEdit()
        form_layout.addWidget(self.name_input, 0, 1)
        form_layout.addWidget(QLabel("Descrição:"), 1, 0)
        self.description_input = QLineEdit()
        form_layout.addWidget(self.description_input, 1, 1)
        form_layout.addWidget(QLabel("Preço:*"), 0, 2)
        self.price_input = QDoubleSpinBox()
        self.price_input.setDecimals(2)
        self.price_input.setMinimum(0.0)
        self.price_input.setMaximum(99999.99)
        self.price_input.setPrefix("R$ ")
        form_layout.addWidget(self.price_input, 0, 3)
        form_layout.addWidget(QLabel("Categoria:"), 1, 2)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Lanche", "Bebida", "Sobremesa", "Outros"]) # Adicionar categorias conforme necessário
        form_layout.addWidget(self.category_combo, 1, 3)
        form_layout.addWidget(QLabel("Estoque Inicial:*"), 2, 0)
        self.stock_input = QSpinBox()
        self.stock_input.setMinimum(0)
        self.stock_input.setMaximum(9999)
        form_layout.addWidget(self.stock_input, 2, 1)
        form_layout.addWidget(QLabel("Imagem (opcional):"), 2, 2)
        self.image_input = QLineEdit() # Poderia ser um botão para selecionar arquivo
        form_layout.addWidget(self.image_input, 2, 3)
        layout.addWidget(form_frame)
        button_layout = QHBoxLayout()
        button_style = """ QPushButton { padding: 8px 15px; font-size: 14px; border-radius: 4px; } QPushButton:hover { background-color: #e0e0e0; } """
        self.new_button = QPushButton("Novo")
        self.new_button.setStyleSheet(button_style)
        self.new_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.new_button)
        self.save_button = QPushButton("Salvar")
        self.save_button.setStyleSheet(button_style + "QPushButton { background-color: #28a745; color: white; } QPushButton:hover { background-color: #218838; }")
        self.save_button.clicked.connect(self.save_product)
        button_layout.addWidget(self.save_button)
        self.delete_button = QPushButton("Excluir")
        self.delete_button.setStyleSheet(button_style + "QPushButton { background-color: #dc3545; color: white; } QPushButton:hover { background-color: #c82333; }")
        self.delete_button.setEnabled(False) # Habilitar apenas quando item selecionado
        self.delete_button.clicked.connect(self.delete_product)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch() # Empurra os botões para a esquerda
        layout.addLayout(button_layout)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Pesquisar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite nome ou categoria...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6) # ID (oculto), Nome, Preço, Categoria, Estoque, Descrição
        self.products_table.setHorizontalHeaderLabels(["ID", "Nome", "Preço", "Categoria", "Estoque", "Descrição"])
        self.products_table.setColumnHidden(0, True) # Ocultar coluna ID
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # Selecionar linha inteira
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Não editável diretamente
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.itemSelectionChanged.connect(self.on_table_item_selection_changed)
        layout.addWidget(self.products_table)
        self.load_products_to_table() # Carregar dados iniciais

    def load_products_to_table(self):
        search_term = self.search_input.text().lower()
        self.products_table.setRowCount(0)
        products_to_display = [p for p in self.main_window.products if not search_term or search_term in p['name'].lower() or search_term in p['category'].lower()]
        for row, product in enumerate(products_to_display):
            self.products_table.insertRow(row)
            id_item = QTableWidgetItem(str(product['id']))
            id_item.setData(Qt.ItemDataRole.UserRole, product['id'])
            self.products_table.setItem(row, 0, id_item)
            self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 2, QTableWidgetItem(f"R$ {product['price']:.2f}"))
            self.products_table.setItem(row, 3, QTableWidgetItem(product['category']))
            self.products_table.setItem(row, 4, QTableWidgetItem(str(product['stock'])))
            self.products_table.setItem(row, 5, QTableWidgetItem(product['description']))
        self.products_table.resizeColumnsToContents()

    def on_table_item_selection_changed(self):
        selected_items = self.products_table.selectedItems()
        if not selected_items:
            self.clear_form(); self.delete_button.setEnabled(False); return
        selected_row = self.products_table.currentRow()
        # Verifica se a linha selecionada ainda existe (após filtro, por exemplo)
        if selected_row < 0 or selected_row >= self.products_table.rowCount():
             self.clear_form(); self.delete_button.setEnabled(False); return

        id_item = self.products_table.item(selected_row, 0) # Pega o item da célula
        if id_item is None: # Checagem adicional
             self.clear_form(); self.delete_button.setEnabled(False); return

        product_id = id_item.data(Qt.ItemDataRole.UserRole)
        self.selected_product_id = product_id
        product_data = next((p for p in self.main_window.products if p['id'] == product_id), None)
        if product_data:
            self.name_input.setText(product_data['name'])
            self.description_input.setText(product_data['description'])
            self.price_input.setValue(product_data['price'])
            self.category_combo.setCurrentText(product_data['category'])
            self.stock_input.setValue(product_data['stock'])
            self.stock_input.setEnabled(False)
            self.image_input.setText(product_data.get('image', ''))
            self.delete_button.setEnabled(True)
        else: self.clear_form()

    def save_product(self):
        name = self.name_input.text().strip(); description = self.description_input.text().strip()
        price = self.price_input.value(); category = self.category_combo.currentText()
        stock = self.stock_input.value(); image = self.image_input.text().strip()
        if not name or price <= 0:
            QMessageBox.warning(self, "Campos Obrigatórios", "Nome e Preço (maior que zero) são obrigatórios."); return
        product_data = {'name': name, 'description': description, 'price': price, 'category': category, 'image': image, 'stock': stock }
        if self.selected_product_id is None:
            product_data['id'] = self.main_window.get_next_product_id()
            self.main_window.products.append(product_data)
            QMessageBox.information(self, "Sucesso", f"Produto '{name}' adicionado!")
        else:
            product_data['id'] = self.selected_product_id; found = False
            for i, p in enumerate(self.main_window.products):
                if p['id'] == self.selected_product_id:
                    product_data['stock'] = p['stock'] # Mantém estoque original
                    self.main_window.products[i] = product_data; found = True; break
            if found: QMessageBox.information(self, "Sucesso", f"Produto '{name}' atualizado!")
            else: QMessageBox.critical(self, "Erro", "Erro ao atualizar."); return
        self.main_window.save_products_to_file(); self.load_products_to_table(); self.clear_form()

    def clear_form(self):
        self.selected_product_id = None; self.name_input.clear(); self.description_input.clear()
        self.price_input.setValue(0.0); self.category_combo.setCurrentIndex(0)
        self.stock_input.setValue(0); self.stock_input.setEnabled(True); self.image_input.clear()
        self.products_table.clearSelection(); self.delete_button.setEnabled(False); self.name_input.setFocus()

    def delete_product(self):
        if self.selected_product_id is None: return
        product_to_delete = next((p for p in self.main_window.products if p['id'] == self.selected_product_id), None)
        if not product_to_delete: QMessageBox.critical(self, "Erro", "Produto não encontrado."); self.clear_form(); return
        reply = QMessageBox.question(self, 'Confirmar Exclusão', f"Excluir '{product_to_delete['name']}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.main_window.products.remove(product_to_delete)
            self.main_window.save_products_to_file()
            QMessageBox.information(self, "Sucesso", f"Produto '{product_to_delete['name']}' excluído.")
            self.load_products_to_table(); self.clear_form()

    def filter_table(self): self.load_products_to_table()

class EstoqueTab(QWidget):
    # --- Gerenciamento de Estoque (SIMPLIFICADO) ---
     def __init__(self, main_window): # Recebe a instância principal
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        title_label = QLabel("Gerenciamento de Estoque")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.estoque_table = QTableWidget()
        self.estoque_table.setColumnCount(3) # Produto, Quantidade Atual, Ação
        self.estoque_table.setHorizontalHeaderLabels(["Produto", "Quantidade Atual", "Ações"])
        self.estoque_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.estoque_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.estoque_table.verticalHeader().setVisible(False)
        layout.addWidget(self.estoque_table)
        self.load_estoque()
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

     def load_estoque(self):
        self.estoque_table.setRowCount(0)
        for row, product in enumerate(self.main_window.products):
            self.estoque_table.insertRow(row)
            self.estoque_table.setItem(row, 0, QTableWidgetItem(product['name']))
            self.estoque_table.setItem(row, 1, QTableWidgetItem(str(product['stock'])))
            adjust_button = QPushButton("Ajustar Estoque")
            adjust_button.clicked.connect(lambda checked, p_id=product['id'], p_name=product['name']: self.show_adjust_dialog(p_id, p_name))
            self.estoque_table.setCellWidget(row, 2, adjust_button)
        self.estoque_table.resizeColumnsToContents()

     def show_adjust_dialog(self, product_id, product_name):
        product = next((p for p in self.main_window.products if p['id'] == product_id), None)
        if not product: return
        nova_qtd, ok = QInputDialog.getInt(self, "Ajustar Estoque", f"Nova quantidade para '{product_name}':\n(Atual: {product['stock']})", product['stock'], 0)
        if ok:
            for i, p in enumerate(self.main_window.products):
                 if p['id'] == product_id: self.main_window.products[i]['stock'] = nova_qtd; break
            self.main_window.save_products_to_file(); self.load_estoque()
            QMessageBox.information(self, "Sucesso", f"Estoque de '{product_name}' ajustado para {nova_qtd}.")

class VendasTab(QWidget): # Gerente
    #
     def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.carrinho_local = []
        layout = QGridLayout(self)
        title_label = QLabel("Registro/Consulta de Vendas (Gerente)")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label, 0, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        add_item_frame = QFrame(); add_item_frame.setFrameShape(QFrame.Shape.StyledPanel); add_item_layout = QGridLayout(add_item_frame)
        add_item_layout.addWidget(QLabel("Produto:"), 0, 0)
        self.produto_combo = QComboBox()
        self.update_products_combo() # Carrega produtos iniciais
        add_item_layout.addWidget(self.produto_combo, 0, 1)
        add_item_layout.addWidget(QLabel("Quantidade:"), 1, 0)
        self.quantidade_spinbox = QSpinBox(); self.quantidade_spinbox.setMinimum(1)
        add_item_layout.addWidget(self.quantidade_spinbox, 1, 1)
        self.adicionar_button = QPushButton("Adicionar ao Carrinho"); self.adicionar_button.clicked.connect(self.adicionar_ao_carrinho_local)
        add_item_layout.addWidget(self.adicionar_button, 2, 0, 1, 2)
        layout.addWidget(add_item_frame, 1, 0, 1, 2)
        cart_frame = QFrame(); cart_frame.setFrameShape(QFrame.Shape.StyledPanel); cart_layout = QVBoxLayout(cart_frame)
        cart_layout.addWidget(QLabel("Carrinho:"))
        self.carrinho_table = QTableWidget(); self.carrinho_table.setColumnCount(3); self.carrinho_table.setHorizontalHeaderLabels(["Produto", "Qtd", "Preço"])
        cart_layout.addWidget(self.carrinho_table)
        self.finalizar_button = QPushButton("Finalizar Venda"); self.finalizar_button.clicked.connect(self.finalizar_venda_local)
        cart_layout.addWidget(self.finalizar_button)
        layout.addWidget(cart_frame, 1, 2, 1, 2)
        layout.setRowStretch(2, 1); layout.setColumnStretch(0, 1); layout.setColumnStretch(1, 1); layout.setColumnStretch(2, 1); layout.setColumnStretch(3, 1)


     def update_products_combo(self): # Atualiza o combo se a lista de produtos mudar
         current_text = self.produto_combo.currentText()
         self.produto_combo.clear()
         # Adiciona apenas produtos com estoque > 0 ao combo de vendas
         self.produto_combo.addItems([p['name'] for p in self.main_window.products if p['stock'] > 0])
         index = self.produto_combo.findText(current_text)
         if index >= 0:
             self.produto_combo.setCurrentIndex(index)
         elif self.produto_combo.count() > 0:
             self.produto_combo.setCurrentIndex(0) # Seleciona o primeiro se o anterior não existe mais

     def adicionar_ao_carrinho_local(self):
        product_name = self.produto_combo.currentText(); quantity = self.quantidade_spinbox.value()
        if quantity <= 0 or not product_name: return
        product_data = next((p for p in self.main_window.products if p['name'] == product_name), None)
        if not product_data: QMessageBox.warning(self, "Erro", "Produto não encontrado."); return
        # Verifica estoque ANTES de adicionar ao carrinho local
        estoque_disponivel = product_data['stock']
        quantidade_no_carrinho = sum(item['quantidade'] for item in self.carrinho_local if item['produto'] == product_name)
        if estoque_disponivel < quantidade_no_carrinho + quantity:
            QMessageBox.warning(self, "Erro", f"Estoque insuficiente para {product_name}. Disponível: {estoque_disponivel}, No carrinho: {quantidade_no_carrinho}")
            return

        price = product_data['price']
        # Atualiza quantidade se já existe no carrinho local
        item_exists = False
        for item in self.carrinho_local:
            if item['produto'] == product_name:
                item['quantidade'] += quantity
                item_exists = True
                break
        if not item_exists:
            self.carrinho_local.append({'produto': product_name, 'quantidade': quantity, 'preco': price})

        self.atualizar_carrinho_local(); self.quantidade_spinbox.setValue(1)

     def atualizar_carrinho_local(self):
        self.carrinho_table.setRowCount(len(self.carrinho_local))
        for i, item in enumerate(self.carrinho_local):
            self.carrinho_table.setItem(i, 0, QTableWidgetItem(item['produto'])); self.carrinho_table.setItem(i, 1, QTableWidgetItem(str(item['quantidade']))); self.carrinho_table.setItem(i, 2, QTableWidgetItem(f"R${item['preco']:.2f}"))
        self.carrinho_table.resizeColumnsToContents()

     def finalizar_venda_local(self):
        if not self.carrinho_local: return
        total = sum(item['quantidade'] * item['preco'] for item in self.carrinho_local)
        metodo_pagamento, ok = QInputDialog.getText(self, "Pagamento", f"Total: R$ {total:.2f}\nMétodo de Pagamento:")
        if ok and metodo_pagamento:
            # Passar uma cópia dos itens para não modificar o carrinho local antes de salvar
            itens_venda = [item.copy() for item in self.carrinho_local]
            self.main_window.registrar_venda_historico(total, metodo_pagamento, itens_venda)
            QMessageBox.information(self, "Sucesso", "Venda registrada!")
            self.carrinho_local = []; self.atualizar_carrinho_local(); self.update_products_combo()
        elif ok and not metodo_pagamento: QMessageBox.warning(self, "Erro", "Método de pagamento não informado.")

class FiscalTab(QWidget):
    # ... (código da FiscalTab) ...
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title_label = QLabel("Módulo Fiscal")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        gerar_nfe_btn = QPushButton("Gerar Nota Fiscal Eletrônica (NF-e)")
        gerar_nfce_btn = QPushButton("Gerar Nota Fiscal de Consumidor Eletrônica (NFC-e)")
        consultar_impostos_btn = QPushButton("Consultar Impostos")
        layout.addWidget(gerar_nfe_btn); layout.addWidget(gerar_nfce_btn); layout.addWidget(consultar_impostos_btn)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

class ConfiguracoesTab(QWidget):
    # Modificar o __init__ para receber main_window
    def __init__(self, main_window): # <<< RECEBE main_window
        super().__init__()
        self.main_window = main_window # <<< ARMAZENA main_window

        layout = QGridLayout(self)
        title_label = QLabel("Configurações do Sistema")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title_label, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Configurações existentes ---
        layout.addWidget(QLabel("Nome da Lanchonete:"), 1, 0)
        layout.addWidget(QLineEdit("MR Lanches"), 1, 1)
        layout.addWidget(QLabel("Endereço:"), 2, 0)
        layout.addWidget(QLineEdit("Rua Exemplo, 123"), 2, 1)
        layout.addWidget(QLabel("Taxa de Serviço (%):"), 3, 0)
        tax_spin = QSpinBox()
        tax_spin.setSuffix(" %")
        layout.addWidget(tax_spin, 3, 1)

        save_button = QPushButton("Salvar Configurações")
        save_button.setObjectName("primaryButton")
        save_button.setStyleSheet("padding: 8px 15px; font-weight: bold;")
        # save_button.clicked.connect(self.save_settings) # Conectar a uma função
        layout.addWidget(save_button, 4, 0, 1, 2)

        # --- SEÇÃO DE AÇÕES PERIGOSAS ---
        layout.addWidget(QLabel("Ações do Sistema:"), 5, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setRowStretch(6, 1) # Adiciona espaço antes do botão perigoso

        self.clear_sales_button = QPushButton("Zerar Histórico de Vendas")
        # Estilo de perigo (vermelho) - Defina #dangerButton no seu QSS ou use estilo inline
        self.clear_sales_button.setObjectName("dangerButton")
        self.clear_sales_button.setStyleSheet("""
            QPushButton#dangerButton { background-color: #dc3545; color: white; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold; }
            QPushButton#dangerButton:hover { background-color: #c82333; }
            QPushButton#dangerButton:pressed { background-color: #bd2130; }
        """)
        self.clear_sales_button.clicked.connect(self.confirm_clear_sales_history) # Conecta ao método de confirmação
        layout.addWidget(self.clear_sales_button, 7, 0, 1, 2) # Adiciona o botão

        layout.setRowStretch(8, 5) # Adiciona mais espaço abaixo
    def confirm_clear_sales_history(self):
        """Exibe um diálogo de confirmação MUITO claro antes de zerar as vendas."""
        confirm_msg = (
            "<b>ATENÇÃO! AÇÃO IRREVERSÍVEL!</b><br><br>"
            "Você tem certeza ABSOLUTA que deseja apagar TODO o histórico de vendas?<br><br>"
            "Todos os registros de vendas serão permanentemente removidos e não poderão ser recuperados.<br><br>"
            "<b>Digite 'SIM' (em maiúsculas) para confirmar:</b>"
        )

        # Usamos QInputDialog para pegar o texto de confirmação
        text, ok = QInputDialog.getText(
            self,
            "Confirmar Exclusão Total de Vendas",
            confirm_msg,
            QLineEdit.EchoMode.Normal, # Modo normal de texto
            "" # Texto inicial vazio
        )

        if ok and text == "SIM":
            # Segunda confirmação (redundante, mas para segurança extra)
            reply = QMessageBox.warning(
                self,
                "Confirmação Final",
                "Esta é sua última chance. Zerar o histórico de vendas?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No # Botão padrão é Não
            )
            if reply == QMessageBox.StandardButton.Yes:
                print("Confirmação recebida. Solicitando limpeza de vendas...")
                if hasattr(self.main_window, 'clear_sales_data'):
                    self.main_window.clear_sales_data() # Chama a função na janela principal
                else:
                    QMessageBox.critical(self, "Erro Interno", "A função para limpar dados não foi encontrada.")
            else:
                QMessageBox.information(self, "Cancelado", "A operação foi cancelada.")
        elif ok: # Se clicou OK mas não digitou SIM
            QMessageBox.warning(self, "Confirmação Inválida", "A confirmação 'SIM' não foi digitada corretamente. Operação cancelada.")
        else: # Se clicou Cancelar no QInputDialog
             QMessageBox.information(self, "Cancelado", "A operação foi cancelada.")

# --- Aba Financeiro/Relatórios (Atualizada) ---
class FinanceiroTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.filtered_sales_data = [] # <<< INICIALIZA A LISTA AQUI (Correto)
        self.current_report_total = 0.0 
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title_label = QLabel("Relatório de Vendas")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #343a40;")
        layout.addWidget(title_label)

        # --- Filtros ---
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0, 5, 0, 5)

        filter_layout.addWidget(QLabel("Período:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Hoje", "Ontem", "Esta Semana", "Este Mês", "Período Específico"])
        self.period_combo.currentIndexChanged.connect(self.toggle_date_edits)
        filter_layout.addWidget(self.period_combo)

        self.start_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setVisible(False)
        self.start_label = QLabel(" De:")
        self.start_label.setVisible(False)
        self.start_date_edit.setFixedWidth(120)
        filter_layout.addWidget(self.start_label)
        filter_layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setVisible(False)
        self.end_label = QLabel(" Até:")
        self.end_label.setVisible(False)
        self.end_date_edit.setFixedWidth(120)
        filter_layout.addWidget(self.end_label)
        filter_layout.addWidget(self.end_date_edit)

        self.generate_button = QPushButton("Gerar Relatório")
        self.generate_button.setStyleSheet("padding: 5px 10px;")
        # Conecta ao método CORRETO generate_report
        self.generate_button.clicked.connect(self.generate_report)
        filter_layout.addWidget(self.generate_button)

        # Botão Exportar
        self.export_button = QPushButton("Exportar Excel")
        self.export_button.setStyleSheet("padding: 5px 10px; background-color: #196F3D; color: white;")
        self.export_button.clicked.connect(self.export_to_excel)
        # <<< CORREÇÃO: Começa desabilitado
        self.export_button.setEnabled(False)
        filter_layout.addWidget(self.export_button)

        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # --- Tabela de Vendas ---
        self.sales_report_table = QTableWidget()
        self.sales_report_table.setColumnCount(5)
        self.sales_report_table.setHorizontalHeaderLabels(["Data", "Produtos", "Qtd Itens", "Método Pgto", "Total (R$)"])
        self.sales_report_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sales_report_table.setAlternatingRowColors(True)
        self.sales_report_table.verticalHeader().setVisible(False)
        self.sales_report_table.setStyleSheet("""
            QTableWidget { border: 1px solid #ccc; }
            QHeaderView::section { background-color: #eee; padding: 4px; border: 1px solid #ccc; font-weight: bold; }
        """)
        layout.addWidget(self.sales_report_table)

        # --- Totais do Relatório ---
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        totals_layout.addWidget(QLabel("Total Vendas no Período:"))
        self.total_periodo_label = QLabel("R$ 0.00")
        self.total_periodo_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #28a745;")
        totals_layout.addWidget(self.total_periodo_label)
        layout.addLayout(totals_layout)

    def toggle_date_edits(self, index):
        show_dates = (self.period_combo.currentText() == "Período Específico")
        self.start_label.setVisible(show_dates)
        self.start_date_edit.setVisible(show_dates)
        self.end_label.setVisible(show_dates)
        self.end_date_edit.setVisible(show_dates)

    # <<< CORREÇÃO: Apenas UMA definição de get_date_range >>>
    def get_date_range(self):
        """Retorna a data inicial e final com base na seleção do combo."""
        period = self.period_combo.currentText()
        today = QDate.currentDate()
        start_date = today
        end_date = today

        if period == "Hoje":
            pass # Já definido
        elif period == "Ontem":
            start_date = today.addDays(-1)
            end_date = start_date
        elif period == "Esta Semana":
            # Ajuste para considerar o início da semana (Domingo=7, Segunda=1)
            # Qt.DayOfWeek retorna 1 para segunda, 7 para domingo.
            # Para começar no Domingo: today.dayOfWeek() % 7
            # Para começar na Segunda: today.dayOfWeek() - 1
            start_of_week_offset = today.dayOfWeek() - 1 # Começa na Segunda
            # Ou: start_of_week_offset = today.dayOfWeek() % 7 # Começa no Domingo
            start_date = today.addDays(-start_of_week_offset)
            end_date = today # Até hoje
        elif period == "Este Mês":
            start_date = QDate(today.year(), today.month(), 1)
            end_date = today
        elif period == "Período Específico":
            start_date = self.start_date_edit.date()
            end_date = self.end_date_edit.date()
            if start_date > end_date:
                QMessageBox.warning(self, "Datas Inválidas", "A data inicial não pode ser posterior à data final.")
                return None, None # Retorna None para indicar erro

        # Para criar QDateTime a partir de QDate, forneça também um QTime.
        # Para start_dt, queremos o início do dia (00:00:00).
        # Para end_dt, queremos o fim do dia (23:59:59).
        start_dt = QDateTime(start_date, QTime(0, 0, 0)) # Adiciona QTime para o início do dia
        end_dt = QDateTime(end_date, QTime(23, 59, 59)) # Adiciona QTime para o fim do dia

        return start_dt, end_dt

    # <<< CORREÇÃO: REMOVIDA a definição placeholder de generate_report >>>
    # Esta é a definição CORRETA e ÚNICA de generate_report
    def generate_report(self):
        """Lê vendas.json, filtra e preenche a tabela."""
        print("Gerando Relatório Financeiro...") # Debug
        self.sales_report_table.setRowCount(0)
        total_periodo = 0.0
        self.filtered_sales_data = [] # <<< Limpa os dados filtrados ANTES de começar
        self.export_button.setEnabled(False) # <<< Desabilita exportação até ter dados

        start_dt, end_dt = self.get_date_range()
        # Verifica se get_date_range retornou datas válidas
        if start_dt is None or end_dt is None:
             # A mensagem de erro já foi mostrada em get_date_range
             return # Interrompe a geração do relatório

        try:
            if os.path.exists(self.main_window.SALES_FILE):
                with open(self.main_window.SALES_FILE, "r", encoding='utf-8') as f:
                    sales_data = json.load(f)

                # Filtra os dados ANTES de ordenar e popular a tabela
                for sale in sales_data:
                     if 'data' in sale: # Verifica se chave existe
                        sale_dt_str = sale['data']
                        # Tenta parsear com formatos comuns ISO
                        sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODate)
                        if not sale_dt.isValid():
                            sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODateWithMs) # Tenta com milissegundos

                        if sale_dt.isValid() and start_dt <= sale_dt <= end_dt:
                            self.filtered_sales_data.append(sale) # <<< Adiciona à lista filtrada
                     else:
                         print(f"Aviso: Venda sem chave 'data' encontrada: {sale}")

                # Ordena os dados filtrados (mais recentes primeiro)
                self.filtered_sales_data.sort(key=lambda x: QDateTime.fromString(x['data'], Qt.DateFormat.ISODate) if QDateTime.fromString(x['data'], Qt.DateFormat.ISODate).isValid() else QDateTime.fromString(x['data'], Qt.DateFormat.ISODateWithMs), reverse=True)

                # Popula a tabela com os dados JÁ filtrados e ordenados
                for row, sale in enumerate(self.filtered_sales_data):
                    self.sales_report_table.insertRow(row)

                    # Re-parsear a data para exibição consistente
                    sale_dt_display = QDateTime.fromString(sale['data'], Qt.DateFormat.ISODate)
                    if not sale_dt_display.isValid():
                         sale_dt_display = QDateTime.fromString(sale['data'], Qt.DateFormat.ISODateWithMs)
                    date_str = sale_dt_display.toString("dd/MM/yyyy HH:mm") if sale_dt_display.isValid() else sale['data'] # Fallback
                    self.sales_report_table.setItem(row, 0, QTableWidgetItem(date_str))

                    # Itens da venda
                    item_names = [f"{item.get('produto','N/A')} ({item.get('quantidade', 0)})" for item in sale.get('itens', [])]
                    self.sales_report_table.setItem(row, 1, QTableWidgetItem(", ".join(item_names)))

                    # Quantidade total de itens
                    total_items_count = sum(item.get('quantidade', 0) for item in sale.get('itens', []))
                    self.sales_report_table.setItem(row, 2, QTableWidgetItem(str(total_items_count)))

                    # Método de pagamento
                    self.sales_report_table.setItem(row, 3, QTableWidgetItem(sale.get('metodo_pagamento', 'N/A')))

                    # Total da venda
                    total_sale = sale.get('total', 0.0)
                    total_item = QTableWidgetItem(f"{total_sale:.2f}")
                    total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.sales_report_table.setItem(row, 4, total_item)

                    total_periodo += total_sale

        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
            error_msg = f"Erro ao ler ou processar {self.main_window.SALES_FILE} para relatório: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Erro ao Gerar Relatório", error_msg)
        except Exception as e: # Captura outras exceções inesperadas
            error_msg = f"Erro inesperado ao gerar relatório: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Erro Inesperado", error_msg)


        self.sales_report_table.resizeColumnsToContents()
        self.total_periodo_label.setText(f"R$ {total_periodo:.2f}")
        # <<< CORREÇÃO: Habilita exportação APENAS se houver dados filtrados
        self.export_button.setEnabled(len(self.filtered_sales_data) > 0)
        print(f"Relatório gerado com {len(self.filtered_sales_data)} vendas.") # Debug

    def load_data(self):
        """Método para ser chamado quando a aba se torna visível."""
        print("Carregando dados da Aba Financeiro...")
        # Gera o relatório com os filtros padrões (Hoje) ao carregar a aba
        self.generate_report()

    # <<< --- MÉTODO PARA EXPORTAR (Parece correto, depende de generate_report funcionar) --- >>>
        # <<< --- MÉTODO PARA EXPORTAR (MODIFICADO PARA USAR TOTAL DO RELATÓRIO) --- >>>
    def export_to_excel(self):
        """Exporta os dados do relatório atual e adiciona o total do período ao final."""
        if not self.filtered_sales_data:
            QMessageBox.information(self, "Sem Dados", "Gere um relatório com dados antes de exportar.")
            return

        # --- 1. Prepara os dados do relatório principal (Igual a antes) ---
        print("--- Preparando dados do relatório para exportação...")
        data_for_export = []
        for sale in self.filtered_sales_data:
            sale_dt = QDateTime.fromString(sale.get('data', ''), Qt.DateFormat.ISODate)
            if not sale_dt.isValid():
                sale_dt = QDateTime.fromString(sale.get('data', ''), Qt.DateFormat.ISODateWithMs)
            date_str = sale_dt.toString("dd/MM/yyyy HH:mm") if sale_dt.isValid() else sale.get('data', '')
            items_str = ", ".join([f"{item.get('produto','N/A')} ({item.get('quantidade',0)})" for item in sale.get('itens', [])])
            qtd_total = sum(item.get('quantidade', 0) for item in sale.get('itens', []))
            data_for_export.append({
                "Data": date_str,
                "Produtos": items_str,
                "Qtd Itens": qtd_total,
                "Método Pgto": sale.get('metodo_pagamento', 'N/A'),
                "Total (R$)": sale.get('total', 0.0)
            })

        # --- 2. Cria o DataFrame principal (Igual a antes) ---
        try:
            df = pd.DataFrame(data_for_export)
            df['Total (R$)'] = pd.to_numeric(df['Total (R$)'])
            print(f"--- DataFrame principal criado com {len(df)} linhas.")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Criar DataFrame", f"Erro ao preparar dados do relatório:\n{e}")
            return

        # --- 3. Pega o total do relatório já calculado ---
        # REMOVIDO: Bloco que calculava total_vendido_hoje
        report_total = self.current_report_total # <<< USA O VALOR ARMAZENADO
        print(f"--- Usando o total do período do relatório: R$ {report_total:.2f}")

        # --- 4. Adiciona linhas extras ao DataFrame ---
        try:
            # Cria um DataFrame para a linha de espaço
            spacer_row = pd.DataFrame([{}], columns=df.columns)

            # Cria um DataFrame para a linha do total do período
            total_period_row_data = {
                # <<< AJUSTA O RÓTULO >>>
                "Data": ["TOTAL DO PERÍODO:"],
                "Total (R$)": [report_total] # <<< USA A VARIÁVEL report_total
            }
            # Preenche as outras colunas com vazio
            for col in df.columns:
                 if col not in total_period_row_data:
                     total_period_row_data[col] = [""]

            total_period_row = pd.DataFrame(total_period_row_data, columns=df.columns)

            # Concatena os DataFrames
            df = pd.concat([df, spacer_row, total_period_row], ignore_index=True)
            print("--- Linhas de resumo (total do período) adicionadas ao DataFrame.")

        except Exception as e_append:
            print(f"--- Aviso: Erro ao adicionar linhas de resumo ao DataFrame: {e_append}")
            # Continua a exportação apenas com os dados principais se falhar aqui

        # --- 5. Salva no Excel (Igual a antes) ---
        print("--- Solicitando local para salvar o arquivo Excel...")
        default_filename = f"Relatorio_Vendas_{QDate.currentDate().toString('yyyyMMdd')}.xlsx"
        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(download_path):
            download_path = os.path.expanduser("~")
        filePath, _ = QFileDialog.getSaveFileName(
            self, "Salvar Relatório Excel", os.path.join(download_path, default_filename),
            "Arquivos Excel (*.xlsx);;Todos os Arquivos (*)"
        )
        if filePath:
            if not filePath.lower().endswith('.xlsx'): filePath += '.xlsx'
            try:
                print(f"--- Salvando DataFrame no arquivo: {filePath}")
                df.to_excel(filePath, index=False, sheet_name="RelatorioVendas")
                QMessageBox.information(self, "Exportação Concluída", f"Relatório salvo com sucesso em:\n{filePath}")
                print("--- Exportação concluída com sucesso.")
            except ImportError:
                 QMessageBox.critical(self, "Erro de Dependência", "A biblioteca 'openpyxl' é necessária para exportar para .xlsx.\nInstale com: pip install openpyxl")
                 print("--- ERRO: Dependência 'openpyxl' não encontrada.")
            except Exception as e:
                QMessageBox.critical(self, "Erro ao Exportar", f"Não foi possível salvar o arquivo Excel:\n{e}\n\nVerifique se o arquivo não está aberto em outro programa.")
                print(f"--- ERRO ao salvar Excel: {e}")
        else:
            print("--- Exportação cancelada pelo usuário.")

    # Removed duplicate definition of toggle_date_edits

    def get_date_range(self):
        """Retorna a data inicial e final com base na seleção do combo."""
        period = self.period_combo.currentText()
        today = QDate.currentDate()
        start_date = today
        end_date = today

        if period == "Hoje":
            pass # Já definido
        elif period == "Ontem":
            start_date = today.addDays(-1)
            end_date = start_date
        elif period == "Esta Semana":
            start_date = today.addDays(-(today.dayOfWeek() % 7)) # Domingo
            end_date = today # Até hoje
        elif period == "Este Mês":
            start_date = QDate(today.year(), today.month(), 1)
            end_date = today
        elif period == "Período Específico":
            start_date = self.start_date_edit.date()
            end_date = self.end_date_edit.date()
            if start_date > end_date:
                QMessageBox.warning(self, "Datas Inválidas", "A data inicial não pode ser posterior à data final.")
                return None, None

        # --- CORREÇÃO AQUI ---
        # Para criar QDateTime a partir de QDate, forneça também um QTime.
        # Para start_dt, queremos o início do dia (00:00:00).
        # Para end_dt, queremos o fim do dia (23:59:59).
        start_dt = QDateTime(start_date, QTime(0, 0, 0)) # Adiciona QTime para o início do dia
        end_dt = QDateTime(end_date, QTime(23, 59, 59))
        # --- FIM DA CORREÇÃO ---

        return start_dt, end_dt


        # <<< Função generate_report com LOGGING DETALHADO >>>
    def generate_report(self):
        """Lê vendas.json, filtra, preenche a tabela e loga erros detalhadamente."""
        print("--- Iniciando generate_report ---") # Mais específico
        self.sales_report_table.setRowCount(0)
        total_periodo = 0.0
        self.filtered_sales_data = []
        self.export_button.setEnabled(False) # Garante que começa desabilitado

        print("--- Obtendo intervalo de datas...")
        start_dt, end_dt = self.get_date_range()
        if start_dt is None or end_dt is None:
             print("--- Erro: Intervalo de datas inválido retornado por get_date_range.")
             # Mensagem de erro já foi mostrada em get_date_range
             return # Interrompe a geração

        print(f"--- Intervalo de datas definido: {start_dt.toString()} a {end_dt.toString()}")
        print(f"--- Lendo arquivo: {self.main_window.SALES_FILE}")

        try:
            if os.path.exists(self.main_window.SALES_FILE):
                with open(self.main_window.SALES_FILE, "r", encoding='utf-8') as f:
                    sales_data = json.load(f)
                print(f"--- Arquivo lido. {len(sales_data)} registros encontrados.")

                # --- Fase de Filtragem ---
                print("--- Iniciando filtragem dos dados...")
                sales_processed_count = 0
                for sale_index, sale in enumerate(sales_data):
                    sales_processed_count += 1
                    try: # Try específico para processar UM registro de venda
                        if 'data' not in sale:
                            print(f"--- ALERTA (Registro {sale_index}): Chave 'data' ausente. Registro: {sale}")
                            continue # Pula este registro

                        sale_dt_str = sale['data']
                        if not isinstance(sale_dt_str, str):
                            print(f"--- ERRO (Registro {sale_index}): Valor da chave 'data' não é string: '{sale_dt_str}'. Registro: {sale}")
                            continue # Pula este registro

                        # Tenta parsear a data
                        sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODate)
                        if not sale_dt.isValid():
                            sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODateWithMs)

                        if not sale_dt.isValid():
                            print(f"--- ALERTA (Registro {sale_index}): Não foi possível parsear a data: '{sale_dt_str}'. Registro: {sale}")
                            # Decide se quer pular ou continuar mesmo sem data válida
                            continue # Pula se a data for crucial para o filtro

                        # Aplica o filtro de data
                        if start_dt <= sale_dt <= end_dt:
                            # Verificações adicionais opcionais antes de adicionar:
                            if 'total' not in sale or not isinstance(sale.get('total'), (int, float)):
                                print(f"--- ALERTA (Registro {sale_index}): Chave 'total' ausente ou não numérica. Usando 0.0. Registro: {sale}")
                                sale['total'] = sale.get('total', 0.0) # Tenta usar ou default 0.0
                            # Adiciona à lista filtrada
                            self.filtered_sales_data.append(sale)

                    except Exception as e_filter:
                        print(f"--- ERRO INESPERADO ao processar registro {sale_index} na filtragem: {e_filter}\nRegistro com erro: {sale}")
                        # Decide se quer parar tudo ou só pular este registro
                        continue # Pula o registro problemático

                print(f"--- Filtragem concluída. {len(self.filtered_sales_data)} registros correspondem ao período de {sales_processed_count} processados.")

                # --- Fase de Ordenação ---
                if self.filtered_sales_data:
                    print("--- Iniciando ordenação dos dados filtrados...")
                    try:
                        # Usa .get('data', '') para evitar KeyError se 'data' sumiu de alguma forma
                        self.filtered_sales_data.sort(
                            key=lambda x: QDateTime.fromString(x.get('data', ''), Qt.DateFormat.ISODate) if QDateTime.fromString(x.get('data', ''), Qt.DateFormat.ISODate).isValid() else QDateTime.fromString(x.get('data', ''), Qt.DateFormat.ISODateWithMs),
                            reverse=True
                        )
                        print("--- Ordenação concluída.")
                    except Exception as e_sort:
                        print(f"--- ERRO durante a ordenação: {e_sort}. A tabela será populada com dados não ordenados.")
                        # Não para, mas avisa. A tabela ainda pode ser útil.

                # --- Fase de População da Tabela ---
                print("--- Iniciando população da tabela...")
                rows_added = 0
                for row, sale in enumerate(self.filtered_sales_data):
                    try: # Try específico para popular UMA linha da tabela
                        self.sales_report_table.insertRow(row)
                        rows_added += 1

                        # Data
                        sale_dt_display_str = sale.get('data', 'Data Inválida')
                        sale_dt_display = QDateTime.fromString(sale_dt_display_str, Qt.DateFormat.ISODate)
                        if not sale_dt_display.isValid():
                            sale_dt_display = QDateTime.fromString(sale_dt_display_str, Qt.DateFormat.ISODateWithMs)
                        display_date = sale_dt_display.toString("dd/MM/yyyy HH:mm") if sale_dt_display.isValid() else sale_dt_display_str
                        self.sales_report_table.setItem(row, 0, QTableWidgetItem(display_date))

                        # Itens
                        items_list = sale.get('itens', [])
                        if not isinstance(items_list, list):
                            print(f"--- ALERTA (Linha {row}): 'itens' não é uma lista. Registro: {sale}")
                            items_list = [] # Usa lista vazia
                        item_names = [f"{item.get('produto','N/A')} ({item.get('quantidade', 0)})" for item in items_list]
                        self.sales_report_table.setItem(row, 1, QTableWidgetItem(", ".join(item_names)))

                        # Qtd Itens
                        total_items_count = sum(item.get('quantidade', 0) for item in items_list if isinstance(item.get('quantidade'), int)) # Soma apenas inteiros
                        self.sales_report_table.setItem(row, 2, QTableWidgetItem(str(total_items_count)))

                        # Método Pgto
                        self.sales_report_table.setItem(row, 3, QTableWidgetItem(sale.get('metodo_pagamento', 'N/A')))

                        # Total (R$)
                        total_sale = sale.get('total', 0.0)
                        if not isinstance(total_sale, (int, float)):
                             print(f"--- ALERTA (Linha {row}): 'total' não é numérico: {total_sale}. Usando 0.0. Registro: {sale}")
                             total_sale = 0.0 # Default seguro
                        total_item = QTableWidgetItem(f"{total_sale:.2f}")
                        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                        self.sales_report_table.setItem(row, 4, total_item)

                        total_periodo += total_sale # Acumula o total

                    except Exception as e_table:
                        print(f"--- ERRO INESPERADO ao popular linha {row} da tabela: {e_table}\nRegistro: {sale}")
                        # Tenta adicionar uma linha de erro na tabela para feedback visual
                        try:
                            # Remove a linha parcialmente inserida se `insertRow` foi chamado mas falhou depois
                            if rows_added > self.sales_report_table.rowCount():
                                self.sales_report_table.removeRow(row)

                            error_row_index = self.sales_report_table.rowCount()
                            self.sales_report_table.insertRow(error_row_index)
                            error_item = QTableWidgetItem(f"Erro ao carregar dados desta venda (Registro Original Índice: {sale_index}): {e_table}")
                            error_item.setForeground(Qt.GlobalColor.red)
                            self.sales_report_table.setItem(error_row_index, 0, error_item)
                            self.sales_report_table.setSpan(error_row_index, 0, 1, self.sales_report_table.columnCount())
                        except Exception as e_table_fallback:
                             print(f"--- ERRO ADICIONAL ao tentar adicionar linha de erro na tabela: {e_table_fallback}")
                        continue # Pula para o próximo registro filtrado

                print(f"--- População da tabela concluída. {self.sales_report_table.rowCount()} linhas adicionadas/processadas.")

            else: # Caso o arquivo vendas.json não exista
                print(f"--- Arquivo {self.main_window.SALES_FILE} não encontrado.")
                QMessageBox.information(self, "Arquivo Não Encontrado", f"O arquivo de histórico de vendas ({self.main_window.SALES_FILE}) não foi encontrado.")

        except FileNotFoundError:
            print(f"--- ERRO CRÍTICO: Arquivo {self.main_window.SALES_FILE} não encontrado (verificação inicial falhou?).")
            QMessageBox.critical(self, "Erro Fatal", f"Arquivo {self.main_window.SALES_FILE} não encontrado.")
            return # Para a execução
        except json.JSONDecodeError as e_json:
            print(f"--- ERRO CRÍTICO: Falha ao decodificar JSON do arquivo {self.main_window.SALES_FILE}: {e_json}")
            QMessageBox.critical(self, "Erro de Arquivo", f"O arquivo de vendas ({self.main_window.SALES_FILE}) parece estar corrompido ou mal formatado.\n\nDetalhe: {e_json}")
            return # Para a execução
        except Exception as e_main:
            print(f"--- ERRO CRÍTICO INESPERADO na leitura/processamento principal: {e_main}")
            QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro inesperado ao gerar o relatório:\n{e_main}")
            return # Para a execução

        # --- Finalização ---
        print("--- Redimensionando colunas da tabela...")
        self.sales_report_table.resizeColumnsToContents()
        print("--- Atualizando label de total do período...")
        self.total_periodo_label.setText(f"R$ {total_periodo:.2f}")
        self.current_report_total = total_periodo
        print(f"--- Total do período armazenado para exportação: R$ {self.current_report_total:.2f}")

        # Habilita o botão de exportar SOMENTE SE houver dados válidos na lista filtrada
        if self.filtered_sales_data:
            print(f"--- Habilitando botão de exportar ({len(self.filtered_sales_data)} registros filtrados).")
            self.export_button.setEnabled(True)
        else:
            print("--- Botão de exportar permanece desabilitado (sem dados filtrados).")

        print("--- Fim de generate_report ---")
    def load_data(self):
        """Método para ser chamado quando a aba se torna visível."""
        print("Carregando dados da Aba Financeiro...")
        self.generate_report() # Gera o relatório ao carregar a aba

# --- Diálogo Customizado de Pagamento ---
class PaymentDialog(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.selected_method = None
        self.total_amount = total_amount # Armazena o total
        self.setWindowTitle("Confirmar Pagamento")
        self.setMinimumWidth(450)
        self.setModal(True)

        # --- Estilo (Pode adicionar estilos para os novos campos) ---
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; border-radius: 8px; }
            QLabel#totalLabel { font-size: 24px; font-weight: bold; color: #dc3545; margin-bottom: 5px; } /* Margem reduzida */
            QLabel#infoLabel { font-size: 16px; color: #495057; margin-bottom: 15px; }
            QPushButton#paymentButton { font-size: 14px; padding: 12px 20px; margin: 5px; border: 1px solid #ced4da; border-radius: 5px; background-color: white; min-width: 100px; }
            QPushButton#paymentButton:hover { background-color: #e9ecef; border-color: #adb5bd; }
            QPushButton#paymentButton:pressed { background-color: #dee2e6; }
            QPushButton#paymentButton:checked { background-color: #007bff; color: white; border-color: #0056b3; font-weight: bold;}
            /* Estilos para campos de Troco */
            QWidget#cashPaymentFields { margin-top: 15px; } /* Espaço acima dos campos de dinheiro */
            QLabel#changeLabel { font-size: 16px; font-weight: bold; color: #28a745; margin-top: 5px;} /* Verde para troco */
            QLineEdit#receivedAmountInput { font-size: 14px; padding: 8px; }
            QDialogButtonBox QPushButton { padding: 8px 25px; font-size: 14px; border-radius: 5px; }
        """)

        # --- Layout Principal ---
        layout = QVBoxLayout(self); layout.setSpacing(15); layout.setContentsMargins(25, 25, 25, 25)

        # --- Labels de Total e Instrução ---
        total_label = QLabel(f"Total a Pagar: R$ {self.total_amount:.2f}"); total_label.setObjectName("totalLabel"); total_label.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(total_label)
        info_label = QLabel("Selecione o método de pagamento:"); info_label.setObjectName("infoLabel"); info_label.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(info_label)

        # --- Layout dos Botões de Pagamento ---
        payment_methods_layout = QGridLayout(); payment_methods_layout.setSpacing(10)
        methods = ["Dinheiro", "Cartão Débito", "Cartão Crédito", "PIX"]; self.payment_buttons = {}
        positions = [(i, j) for i in range(2) for j in range(2)]
        for position, name in zip(positions, methods):
            button = QPushButton(name); button.setObjectName("paymentButton"); button.setCheckable(True)
            button.clicked.connect(lambda checked, b=button, n=name: self.on_payment_method_selected(checked, b, n))
            payment_methods_layout.addWidget(button, position[0], position[1]); self.payment_buttons[name] = button
        layout.addLayout(payment_methods_layout)

        # --- Campos para Pagamento em Dinheiro (Inicialmente Ocultos) ---
        self.cash_payment_widget = QWidget() # Container para os campos
        self.cash_payment_widget.setObjectName("cashPaymentFields")
        cash_layout = QGridLayout(self.cash_payment_widget)
        cash_layout.setContentsMargins(0, 0, 0, 0) # Sem margens extras no container
        cash_layout.setSpacing(10)

        cash_layout.addWidget(QLabel("Valor Recebido (R$):"), 0, 0)
        self.received_amount_input = QLineEdit()
        self.received_amount_input.setObjectName("receivedAmountInput")
        # Validador para aceitar apenas números e vírgula/ponto decimal
        self.received_amount_input.setValidator(QDoubleValidator(0.00, 99999.99, 2))
        self.received_amount_input.setPlaceholderText("0,00")
        self.received_amount_input.textChanged.connect(self.calculate_change) # Conecta a mudança de texto
        cash_layout.addWidget(self.received_amount_input, 0, 1)

        cash_layout.addWidget(QLabel("Troco (R$):"), 1, 0)
        self.change_label = QLabel("0.00")
        self.change_label.setObjectName("changeLabel")
        cash_layout.addWidget(self.change_label, 1, 1)

        layout.addWidget(self.cash_payment_widget) # Adiciona o container ao layout principal
        self.cash_payment_widget.setVisible(False) # Começa oculto
        # --- Fim dos Campos de Dinheiro ---

        # --- Botões de Confirmação/Cancelamento ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Confirmar")
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def on_payment_method_selected(self, checked, button, name):
        """Atualiza o método selecionado e mostra/oculta campos de dinheiro."""
        if checked:
            self.selected_method = name
            # Mostra campos de dinheiro APENAS se "Dinheiro" for selecionado
            is_cash = (name == "Dinheiro")
            self.cash_payment_widget.setVisible(is_cash)
            if is_cash:
                self.received_amount_input.setFocus() # Foca no campo valor recebido
                self.received_amount_input.selectAll()
            self.calculate_change() # Recalcula o troco (pode zerar se não for dinheiro)
            # Desmarca outros botões
            for method_name, btn in self.payment_buttons.items():
                if btn != button: btn.setChecked(False)
        else:
            self.selected_method = None
            self.cash_payment_widget.setVisible(False) # Oculta se desmarcar
            self.calculate_change() # Zera o troco

        # Habilita/Desabilita botão OK baseado na seleção
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(self.selected_method is not None)


    def calculate_change(self):
        """Calcula e exibe o troco baseado no valor recebido."""
        if self.selected_method == "Dinheiro" and self.cash_payment_widget.isVisible():
            try:
                # Tenta converter o texto para float, tratando vírgula
                received_text = self.received_amount_input.text().replace(',', '.')
                if not received_text: received_text = "0" # Considera vazio como 0
                received_amount = float(received_text)

                if received_amount >= self.total_amount:
                    change = received_amount - self.total_amount
                    self.change_label.setText(f"{change:.2f}")
                    self.change_label.setStyleSheet("color: #28a745; font-size: 16px; font-weight: bold;") # Verde
                else:
                    # Valor recebido é menor que o total
                    change = self.total_amount - received_amount
                    self.change_label.setText(f"Faltam R$ {change:.2f}")
                    self.change_label.setStyleSheet("color: #dc3545; font-size: 14px; font-weight: bold;") # Vermelho
            except ValueError:
                # Texto inválido (não é número)
                self.change_label.setText("Valor inválido")
                self.change_label.setStyleSheet("color: #ffc107; font-size: 14px; font-weight: bold;") # Amarelo
            except Exception as e:
                print(f"Erro inesperado no cálculo do troco: {e}")
                self.change_label.setText("Erro")
                self.change_label.setStyleSheet("color: #dc3545; font-size: 14px; font-weight: bold;")
        else:
            # Se não for dinheiro ou estiver oculto, zera o troco
            self.change_label.setText("0.00")
            self.change_label.setStyleSheet("color: #28a745; font-size: 16px; font-weight: bold;") # Verde padrão


    def accept(self):
        """Sobrescreve o accept para validar valor recebido se for dinheiro."""
        if not self.selected_method:
            QMessageBox.warning(self, "Seleção Necessária", "Escolha um método de pagamento.")
            return

        if self.selected_method == "Dinheiro":
            try:
                received_text = self.received_amount_input.text().replace(',', '.')
                if not received_text: received_text = "0"
                received_amount = float(received_text)

                if received_amount < self.total_amount:
                    QMessageBox.warning(self, "Valor Insuficiente",
                                        f"O valor recebido (R$ {received_amount:.2f}) é menor que o total a pagar (R$ {self.total_amount:.2f}).")
                    self.received_amount_input.setFocus()
                    self.received_amount_input.selectAll()
                    return # Não fecha o diálogo
            except ValueError:
                 QMessageBox.warning(self, "Valor Inválido", "O valor recebido digitado não é um número válido.")
                 self.received_amount_input.setFocus()
                 self.received_amount_input.selectAll()
                 return # Não fecha o diálogo
            except Exception as e:
                 print(f"Erro inesperado na validação do accept: {e}")
                 QMessageBox.critical(self, "Erro", "Ocorreu um erro ao validar o valor recebido.")
                 return

        # Se passou por todas as validações (ou não é dinheiro)
        super().accept() # Fecha o diálogo com status OK

    def get_selected_method(self):
        """Retorna o método selecionado."""
        return self.selected_method

# --- Fim da Classe PaymentDialog ---


# --- Interface do Caixa (POSInterface - Inalterada) ---
class POSInterface(QWidget):
    
    # Dentro da classe POSInterface

    # Dentro do __init__ da POSInterface

    def __init__(self, main_window, products_data):
        super().__init__()
        self.main_window = main_window
        self.products_list = products_data
        self.current_sale_items = []
        # self.last_highlighted_row = -1 # Descomente se usar o destaque da última linha

        self.setWindowTitle("Ponto de Venda (Caixa)")
        self.setStyleSheet("background-color: #f0f4f8;") # Fundo geral

        main_layout = QHBoxLayout(self); main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- PAINEL ESQUERDO (Itens da Venda) ---
        left_panel = QFrame(); left_panel.setObjectName("posLeftPanel")
        left_panel.setStyleSheet("background-color: white; border-radius: 8px;")
        left_panel_layout = QVBoxLayout(left_panel); left_panel_layout.setContentsMargins(15, 15, 15, 15)
        sale_label = QLabel("Itens da Venda Atual"); sale_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #343a40; margin-bottom: 10px;"); left_panel_layout.addWidget(sale_label)

        self.sale_table = QTableWidget()
        self.sale_table.setColumnCount(4)
        self.sale_table.setHorizontalHeaderLabels(["Produto", "Qtd", "Preço Unit.", "Subtotal"])
        self.sale_table.verticalHeader().setVisible(False)
        self.sale_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sale_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.sale_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sale_table.setShowGrid(False)
        self.sale_table.setAlternatingRowColors(True)
        self.sale_table.setStyleSheet("""
            QTableWidget { border: 1px solid #e0e5ec; border-radius: 5px; gridline-color: transparent; background-color: white; alternate-background-color: #f8fafd; selection-background-color: #cfe2ff; selection-color: #1a2b4d; font-size: 10pt; }
            QTableWidget::item { padding: 8px 5px; border-bottom: 1px solid #e8edf3; }
            QHeaderView::section:horizontal { background-color: #eaf2f8; padding: 8px 5px; border: none; border-bottom: 2px solid #c5d9ed; font-weight: bold; color: #34495e; font-size: 10pt; }
            QHeaderView::section:vertical { border: none; }
            QTableCornerButton::section { background-color: #eaf2f8; border: none; }
        """)
        header = self.sale_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        left_panel_layout.addWidget(self.sale_table, 1)

        total_frame = QFrame(); total_frame.setFrameShape(QFrame.Shape.NoFrame); total_layout = QHBoxLayout(total_frame); total_layout.addStretch()
        total_text_label = QLabel("TOTAL:"); total_text_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #dc3545; margin-right: 5px;")
        self.total_value_label = QLabel("R$ 0.00"); self.total_value_label.setStyleSheet("font-size: 22pt; font-weight: bold; color: #dc3545;")
        total_layout.addWidget(total_text_label); total_layout.addWidget(self.total_value_label); left_panel_layout.addWidget(total_frame)
        main_layout.addWidget(left_panel, 3)

        # --- PAINEL DIREITO (Atalhos e Ações) ---
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel); right_panel_layout.setSpacing(15); right_panel_layout.setContentsMargins(0, 0, 0, 0)

        frame_style = "QFrame { background-color: white; border-radius: 8px; border: 1px solid #dfe6f0; padding: 15px; }"

        # <<< Bloco de Input REMOVIDO >>>

        # -- Sub-Painel de Atalhos --
        shortcuts_frame = QFrame(); shortcuts_frame.setObjectName("posShortcutsFrame")
        shortcuts_frame.setStyleSheet(frame_style)
        shortcuts_layout = QVBoxLayout(shortcuts_frame)
        shortcuts_title = QLabel("Atalhos"); shortcuts_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #343a40; margin-bottom: 5px;"); shortcuts_layout.addWidget(shortcuts_title)
        self.shortcuts_grid_layout = QGridLayout(); self.shortcuts_grid_layout.setSpacing(8); shortcuts_layout.addLayout(self.shortcuts_grid_layout)
        shortcuts_layout.addStretch()
        right_panel_layout.addWidget(shortcuts_frame, 1) # Atalhos expandem

        # -- Sub-Painel de Ações Finais --
        actions_frame = QFrame(); actions_frame.setObjectName("posActionsFrame")
        actions_frame.setStyleSheet(frame_style)
        actions_layout = QVBoxLayout(actions_frame); actions_layout.setSpacing(10)
        self.finalize_button = QPushButton("Finalizar Venda (Enter)"); self.finalize_button.setObjectName("primaryButton"); self.finalize_button.setStyleSheet("QPushButton#primaryButton { background-color: #007bff; color: white; padding: 12px; font-size: 12pt; border: none; border-radius: 5px; font-weight: bold; } QPushButton#primaryButton:hover { background-color: #0056b3; }"); self.finalize_button.setShortcut("Enter"); self.finalize_button.clicked.connect(self.finalize_sale); actions_layout.addWidget(self.finalize_button) # MUDADO shortcut para Enter
        self.cancel_button = QPushButton("Cancelar Venda (F3)"); self.cancel_button.setStyleSheet("background-color: #6c757d; color: white; padding: 8px; font-size: 10pt; border: none; border-radius: 5px;"); self.cancel_button.setShortcut("F3"); self.cancel_button.clicked.connect(self.cancel_sale); actions_layout.addWidget(self.cancel_button)
        right_panel_layout.addWidget(actions_frame)

        main_layout.addWidget(right_panel, 2)

        self.populate_shortcuts()

        # O foco inicial pode ir para o primeiro botão de atalho ou ficar sem foco definido
        # self.product_input.setFocus() # Linha removida

     # --- Funções (populate_shortcuts, add_item_from_shortcut, update_sale_table, etc.) ---
     # <<< Cole as implementações CORRIGIDAS dessas funções aqui >>>
     # (Certifique-se que as chamadas a self.product_input.setFocus() foram removidas
     #  de add_item_from_shortcut e finalize_sale)

    def populate_shortcuts(self):
        print("DEBUG POS: Populando atalhos dinamicamente...")
        while self.shortcuts_grid_layout.count():
            child = self.shortcuts_grid_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        col_count = 3 ; row, col = 0, 0
        shortcut_button_style = """
            QPushButton { background-color: white; color: #0056b3; border: 1px solid #aed6f1; padding: 10px 5px; font-size: 9pt; font-weight: bold; text-align: center; border-radius: 4px; min-height: 55px; max-width: 120px; }
            QPushButton:hover { background-color: #eaf2f8; border-color: #5dade2; }
            QPushButton:pressed { background-color: #d4e6f1; }
            QPushButton:disabled { background-color: #e9ecef; color: #adb5bd; border-color: #dee2e6; }
        """
        products_for_shortcuts = []
        if isinstance(self.products_list, list):
             products_for_shortcuts = [ p for p in self.products_list if isinstance(p, dict) and p.get('name') and p.get('stock', 0) > 0 ]
             products_for_shortcuts.sort(key=lambda x: x.get('name', ''))
        print(f"DEBUG POS: {len(products_for_shortcuts)} produtos com estoque para atalhos.")
        if not products_for_shortcuts:
             no_stock_label = QLabel("Nenhum produto com\nestoque disponível\npara atalhos."); no_stock_label.setAlignment(Qt.AlignmentFlag.AlignCenter); no_stock_label.setStyleSheet("color: grey; font-style: italic;"); self.shortcuts_grid_layout.addWidget(no_stock_label, 0, 0, 1, col_count); return
        for product_data in products_for_shortcuts:
            product_name = product_data.get('name', 'N/A'); stock_count = product_data.get('stock', 0); price = product_data.get('price', 0.0); display_name = product_name.replace(" ", "\n", 1)
            button = QPushButton(display_name); button.setToolTip(f"Adicionar {product_name}\nPreço: R$ {price:.2f}\nEstoque: {stock_count}"); button.setStyleSheet(shortcut_button_style)
            if product_name != 'N/A': button.clicked.connect(lambda checked, name=product_name: self.add_item_from_shortcut(name))
            else: button.setEnabled(False)
            self.shortcuts_grid_layout.addWidget(button, row, col); col += 1;
            if col >= col_count: col = 0; row += 1
        print("DEBUG POS: Botões de atalho populados.")

    def add_item_from_shortcut(self, product_name):
        print(f"DEBUG POS: Atalho clicado: {product_name}"); quantidade = 1
        found_product = next((p for p in self.products_list if isinstance(p, dict) and p.get('name') == product_name), None)
        if not found_product: QMessageBox.warning(self, "Erro Atalho", f"Produto '{product_name}' não encontrado."); return
        stock_disponivel = found_product.get('stock', 0); qtd_no_carrinho = 0
        for item in self.current_sale_items:
             if item['produto'] == product_name: qtd_no_carrinho = item['quantidade']; break
        if stock_disponivel < qtd_no_carrinho + quantidade: QMessageBox.warning(self, "Estoque Insuficiente", f"Estoque de {product_name}: {stock_disponivel}.\nNo carrinho: {qtd_no_carrinho}. Pedido: {quantidade}."); return
        preco_unit = found_product.get('price', 0.0); item_updated = False
        for item in self.current_sale_items:
            if item['produto'] == product_name: item['quantidade'] += quantidade; item_updated = True; break
        if not item_updated: self.current_sale_items.append({'produto': product_name, 'quantidade': quantidade, 'preco_unit': preco_unit})
        self.update_sale_table(); self.update_total_display()
        # self.product_input.setFocus() # REMOVIDO

    def update_sale_table(self):
        # (Cole a implementação de update_sale_table aqui, opcionalmente com destaque)
        # self.last_highlighted_row = -1 # Descomente se usar destaque
        self.sale_table.setRowCount(0); total_carrinho = 0.0
        for row, item_data in enumerate(self.current_sale_items):
            self.sale_table.insertRow(row)
            col_produto = QTableWidgetItem(item_data['produto']); col_qtd = QTableWidgetItem(str(item_data['quantidade']))
            price_val = item_data.get('preco_unit', 0.0); col_preco = QTableWidgetItem(f"R${price_val:.2f}")
            subtotal = item_data['quantidade'] * price_val; col_subtotal = QTableWidgetItem(f"R${subtotal:.2f}")
            col_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.sale_table.setItem(row, 0, col_produto); self.sale_table.setItem(row, 1, col_qtd); self.sale_table.setItem(row, 2, col_preco); self.sale_table.setItem(row, 3, col_subtotal)
            total_carrinho += subtotal
            # Destaque opcional da última linha
            # if row == len(self.current_sale_items) - 1:
            #    for col in range(self.sale_table.columnCount()):
            #         table_item = self.sale_table.item(row, col)
            #         if table_item: table_item.setBackground(QColor("#f0f8ff"))
            #    self.last_highlighted_row = row
        self.total_value_label.setText(f"R$ {total_carrinho:.2f}")
        if self.sale_table.rowCount() > 0: self.sale_table.scrollToBottom()


    def update_total_display(self):
          total = sum(item['preco_unit'] * item['quantidade'] for item in self.current_sale_items)
          self.total_value_label.setText(f"R$ {total:.2f}")

    def finalize_sale(self):
          if not self.current_sale_items: QMessageBox.information(self, "Carrinho Vazio", "Adicione itens antes de finalizar."); return
          total = sum(item['preco_unit'] * item['quantidade'] for item in self.current_sale_items)
          payment_dialog = PaymentDialog(total, self); result = payment_dialog.exec()
          if result == QDialog.DialogCode.Accepted:
              metodo_pagamento = payment_dialog.get_selected_method()
              if metodo_pagamento:
                  itens_para_historico = [{'produto': i['produto'], 'quantidade': i['quantidade'], 'preco': i['preco_unit']} for i in self.current_sale_items]
                  self.main_window.registrar_venda_historico(total, metodo_pagamento, itens_para_historico)
                  QMessageBox.information(self, "Sucesso", f"Venda finalizada!\nTotal: R${total:.2f}\nMétodo: {metodo_pagamento}")
                  self.current_sale_items = []; self.update_sale_table(); self.update_total_display()
                  # self.product_input.setFocus() # REMOVIDO
          else: print("Finalização da venda cancelada pelo usuário.")

    def cancel_sale(self):
          if not self.current_sale_items: return
          reply = QMessageBox.question(self, 'Cancelar Venda','Tem certeza?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
          if reply == QMessageBox.StandardButton.Yes: self.current_sale_items = []; self.update_sale_table(); self.update_total_display(); QMessageBox.information(self, "Cancelado", "Venda cancelada.")

        # Fim do método __init__


    def add_item_to_sale(self):
        produto_input = self.product_input.text().strip(); quantidade = self.quantity_input.value()
        if not produto_input: return
        # Busca na lista de produtos da main_window
        found_product = next((p for p in self.main_window.products if p['name'].lower() == produto_input.lower() or p['name'].lower().startswith(produto_input.lower()) or str(p['id']) == produto_input ), None) # Busca por ID também
        if not found_product: QMessageBox.warning(self, "Erro", f"Produto '{produto_input}' não encontrado."); self.product_input.clear(); self.product_input.setFocus(); return
        found_product_name = found_product['name']
        # Verifica estoque na lista principal
        if found_product['stock'] < quantidade: QMessageBox.warning(self, "Erro", f"Estoque insuficiente para {found_product_name}. Disponível: {found_product['stock']}"); self.product_input.setFocus(); return
        preco_unit = found_product['price'] # Pega preço do produto encontrado

        item_updated = False
        quantidade_total_no_carrinho = 0
        for item in self.current_sale_items:
             if item['produto'] == found_product_name:
                 quantidade_total_no_carrinho = item['quantidade']
                 break

        if found_product['stock'] < quantidade_total_no_carrinho + quantidade:
              QMessageBox.warning(self, "Erro", f"Estoque insuficiente para adicionar mais {quantidade} de {found_product_name}. Disponível: {found_product['stock']}, No carrinho: {quantidade_total_no_carrinho}");
              self.product_input.clear(); self.product_input.setFocus(); return

        for item in self.current_sale_items:
            if item['produto'] == found_product_name:
                item['quantidade'] += quantidade; item_updated = True; break
        if not item_updated:
             self.current_sale_items.append({'produto': found_product_name, 'quantidade': quantidade, 'preco_unit': preco_unit})
        # ATUALIZA UI
        self.update_sale_table()
        self.update_total_display()
        # <<< FIM DA CHAMADA >>>
        self.product_input.clear()
        self.quantity_input.setValue(1)
        self.product_input.setFocus()

    def update_sale_table(self):
        # Estilo base para itens normais (precisa ser definido ou pego do estilo geral)
        normal_item_style = "padding: 8px 5px; border-bottom: 1px solid #e8edf3;"
        # Estilo para o item recém-adicionado (fundo ligeiramente diferente)
        highlight_item_style = "padding: 8px 5px; border-bottom: 1px solid #c5d9ed; background-color: #f0f8ff;" # Azul muito claro (AliceBlue)

        # Limpa estilo da linha anteriormente destacada, se houver
        if hasattr(self, 'last_highlighted_row') and self.last_highlighted_row >= 0 and self.last_highlighted_row < self.sale_table.rowCount():
             for col in range(self.sale_table.columnCount()):
                 item = self.sale_table.item(self.last_highlighted_row, col)
                 if item: # Aplica estilo normal (ou reseta para padrão da tabela)
                     # Se você não definir 'normal_item_style', pode precisar resetar o fundo:
                     # item.setBackground(QColor(Qt.GlobalColor.transparent)) # Ou a cor alternada
                     pass # O estilo geral da tabela já deve cuidar disso ao recriar

        self.sale_table.setRowCount(0) # Limpa a tabela antes de repopular
        total_carrinho = 0.0

        for row, item_data in enumerate(self.current_sale_items):
            self.sale_table.insertRow(row)
            col_produto = QTableWidgetItem(item_data['produto'])
            col_qtd = QTableWidgetItem(str(item_data['quantidade']))
            price_val = item_data.get('preco_unit', 0.0) # <<< CORRIGIDO de 'preco' para 'preco_unit'
            col_preco = QTableWidgetItem(f"R${price_val:.2f}")
            subtotal = item_data['quantidade'] * price_val
            col_subtotal = QTableWidgetItem(f"R${subtotal:.2f}")
            col_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            self.sale_table.setItem(row, 0, col_produto)
            self.sale_table.setItem(row, 1, col_qtd)
            self.sale_table.setItem(row, 2, col_preco)
            self.sale_table.setItem(row, 3, col_subtotal)

            total_carrinho += subtotal

            # <<< DESTACA A ÚLTIMA LINHA >>>
            if row == len(self.current_sale_items) - 1: # Se for a última linha
                for col in range(self.sale_table.columnCount()):
                     table_item = self.sale_table.item(row, col)
                     if table_item:
                         # Aplica a cor de fundo diretamente ao item
                         table_item.setBackground(QColor("#f0f8ff")) # AliceBlue
                self.last_highlighted_row = row # Armazena o índice da linha destacada
            # <<< FIM DO DESTAQUE >>>


        # self.sale_table.resizeColumnsToContents() # Não mais necessário com Stretch/ResizeToContents
        self.total_value_label.setText(f"R$ {total_carrinho:.2f}") # Atualiza o total

        # Garante que a última linha adicionada (se houver) seja visível
        if self.sale_table.rowCount() > 0:
            self.sale_table.scrollToBottom()
    def update_total_display(self): total = sum(item['preco_unit'] * item['quantidade'] for item in self.current_sale_items); self.total_value_label.setText(f"R$ {total:.2f}")
    def finalize_sale(self):
        if not self.current_sale_items: return
        total = sum(item['preco_unit'] * item['quantidade'] for item in self.current_sale_items)

        # --- CORREÇÃO APLICADA ---
        # 1. Cria a instância do diálogo
        payment_dialog = PaymentDialog(total, self)

        # 2. Exibe o diálogo e obtém o resultado (Accepted ou Rejected)
        result = payment_dialog.exec()
        # --- FIM DA CORREÇÃO ---

        # 3. Verifica se o usuário clicou em "Confirmar" (OK) e o diálogo foi aceito
        if result == QDialog.DialogCode.Accepted:
            # Pega o método escolhido DENTRO do if, pois só é relevante se foi aceito
            metodo_pagamento = payment_dialog.get_selected_method()

            # A validação no accept do diálogo já garante que metodo_pagamento não será None aqui.
            # Se chegou aqui, um método válido foi selecionado.
            print(f"Método de pagamento selecionado: {metodo_pagamento}") # Debug
            # Prepara os itens para o histórico
            itens_para_historico = [{'produto': i['produto'], 'quantidade': i['quantidade'], 'preco': i['preco_unit']} for i in self.current_sale_items]
            # Chama o método central para registrar a venda
            self.main_window.registrar_venda_historico(total, metodo_pagamento, itens_para_historico)
            QMessageBox.information(self, "Sucesso", f"Venda finalizada!\nTotal: R${total:.2f}\nMétodo: {metodo_pagamento}")
            # Limpa o carrinho e reseta a interface
            self.current_sale_items = []
            self.update_sale_table()
            self.update_total_display()
            # self.product_input.setFocus()
            # O 'else' que verificava se metodo_pagamento era None foi removido
            # pois a validação interna do diálogo impede essa condição se Accepted.

        else: # Caso result seja Rejected (usuário clicou em Cancelar)
             print("Finalização da venda cancelada pelo usuário.")
        # <<< FIM DA SUBSTITUIÇÃO >>>
    
    # Dentro da classe POSInterface

    # Dentro da classe POSInterface

    def populate_shortcuts(self):
        """Cria e adiciona botões de atalho DINAMICAMENTE ao grid layout
           baseado nos produtos disponíveis com estoque."""
        print("DEBUG POS: Iniciando populate_shortcuts...") # Movido para o início

        # Limpa quaisquer botões antigos
        while self.shortcuts_grid_layout.count():
            child = self.shortcuts_grid_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        col_count = 3 ; row, col = 0, 0
        shortcut_button_style = """...""" # Mantenha seu estilo aqui

        # <<< DEBUG: Verificar a lista original >>>
        print(f"DEBUG POS: Verificando self.products_list (tipo: {type(self.products_list)})")
        if isinstance(self.products_list, list):
            print(f"DEBUG POS: Tamanho de self.products_list: {len(self.products_list)}")
            # Imprime alguns exemplos para verificação (cuidado com listas muito grandes)
            if len(self.products_list) > 0:
                 print(f"DEBUG POS: Exemplo de produto[0]: {self.products_list[0]}")
            if len(self.products_list) > 1:
                 print(f"DEBUG POS: Exemplo de produto[1]: {self.products_list[1]}")
        else:
             print("ERRO POS: self.products_list NÃO é uma lista!")
             # Adiciona label de erro e sai
             error_label = QLabel("Erro interno:\nLista de produtos\ninválida."); error_label.setAlignment(Qt.AlignmentFlag.AlignCenter); error_label.setStyleSheet("color: red;"); self.shortcuts_grid_layout.addWidget(error_label, 0, 0, 1, col_count); return
        # <<< FIM DEBUG >>>

        products_for_shortcuts = []
        if isinstance(self.products_list, list):
             # Critério: Produto é um dicionário, tem nome E TEM ESTOQUE > 0
             products_for_shortcuts = [
                 p for p in self.products_list
                 if isinstance(p, dict) and p.get('name') and p.get('stock', 0) > 0
                 # <<< DEBUG: Verificação individual (descomente se necessário) >>>
                 # and print(f"  - Verificando: {p.get('name')}, Estoque: {p.get('stock', 0)}, Válido: {isinstance(p, dict) and p.get('name') and p.get('stock', 0) > 0}") is None
             ]
             products_for_shortcuts.sort(key=lambda x: x.get('name', ''))

        # <<< DEBUG: Verificar a lista filtrada >>>
        print(f"DEBUG POS: Produtos FILTRADOS para atalhos: {len(products_for_shortcuts)}")
        if len(products_for_shortcuts) > 0:
             print(f"DEBUG POS: Exemplo de produto filtrado[0]: {products_for_shortcuts[0]}")
        # <<< FIM DEBUG >>>


        if not products_for_shortcuts:
             print("DEBUG POS: Nenhum produto encontrado com estoque > 0 para atalhos.") # Mensagem mais específica
             no_stock_label = QLabel("Nenhum produto com\nestoque disponível\npara atalhos.")
             no_stock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
             no_stock_label.setStyleSheet("color: grey; font-style: italic;")
             self.shortcuts_grid_layout.addWidget(no_stock_label, 0, 0, 1, col_count)
             return # Sai da função

        # Cria botões para os produtos selecionados (código como antes)
        for product_data in products_for_shortcuts:
            # ... (criação e adição dos botões) ...
            product_name = product_data.get('name', 'N/A'); stock_count = product_data.get('stock', 0); price = product_data.get('price', 0.0); display_name = product_name.replace(" ", "\n", 1)
            button = QPushButton(display_name); button.setToolTip(f"Adicionar {product_name}\nPreço: R$ {price:.2f}\nEstoque: {stock_count}"); button.setStyleSheet(shortcut_button_style)
            if product_name != 'N/A': button.clicked.connect(lambda checked, name=product_name: self.add_item_from_shortcut(name))
            else: button.setEnabled(False)
            self.shortcuts_grid_layout.addWidget(button, row, col)
            col += 1;
            if col >= col_count: col = 0; row += 1

        print("DEBUG POS: Botões de atalho populados.")
    def add_item_from_shortcut(self, product_name):
        """Adiciona um item ao carrinho a partir de um botão de atalho (qtd=1)."""
        print(f"DEBUG POS: Atalho clicado: {product_name}")
        quantidade = 1 # Atalho sempre adiciona 1 unidade

        # Busca o produto na lista principal (pelo nome exato)
        found_product = next((p for p in self.products_list if isinstance(p, dict) and p.get('name') == product_name), None)

        if not found_product:
             QMessageBox.warning(self, "Erro Atalho", f"Produto '{product_name}' não encontrado nos dados atuais.")
             return

        # Verifica estoque (essencial!)
        stock_disponivel = found_product.get('stock', 0)
        qtd_no_carrinho = 0
        for item in self.current_sale_items:
             if item['produto'] == product_name:
                 qtd_no_carrinho = item['quantidade']
                 break

        if stock_disponivel < qtd_no_carrinho + quantidade:
              QMessageBox.warning(self, "Estoque Insuficiente", f"Estoque insuficiente para adicionar mais {quantidade} de {product_name}.\nDisponível: {stock_disponivel}, No carrinho: {qtd_no_carrinho}")
              return # Não adiciona

        # Pega o preço
        preco_unit = found_product.get('price', 0.0)

        # Atualiza quantidade se já existe, senão adiciona
        item_updated = False
        for item in self.current_sale_items:
            if item['produto'] == product_name:
                item['quantidade'] += quantidade
                item_updated = True
                break
        if not item_updated:
            self.current_sale_items.append({'produto': product_name, 'quantidade': quantidade, 'preco_unit': preco_unit})
        # ATUALIZA UI
        self.update_sale_table()
        self.update_total_display()
        # <<< FIM DA CHAMADA >>>
        # self.product_input.setFocus()

        # Atualiza a tabela e o total
        self.update_sale_table()
        self.update_total_display()
        # Mantém o foco no input principal
        # self.product_input.setFocus()
        # Opcional: Limpar o input após usar atalho?
        # self.product_input.clear()
    def cancel_sale(self):
        if not self.current_sale_items: return
        reply = QMessageBox.question(self, 'Cancelar Venda','Tem certeza?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes: self.current_sale_items = []; self.update_sale_table(); self.update_total_display(); self.product_input.clear(); self.product_input.setFocus(); QMessageBox.information(self, "Cancelado", "Venda cancelada.")


# --- Classe Principal (SistemaLanchonetePremium) ---
class SistemaLanchonetePremium(QWidget):
    # Obtém o diretório onde este script (SistemaLanchonetePremium.py) está localizado
    # Ex: /caminho/para/seu/projeto/src
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Sobe um nível no diretório (para sair da pasta 'src')
    # Ex: /caminho/para/seu/projeto
    base_dir = os.path.abspath(os.path.join(script_dir, '..'))

    # Constrói o caminho completo para os arquivos JSON na pasta pai
    PRODUCTS_FILE = os.path.join(base_dir, "products.json")
    SALES_FILE = os.path.join(base_dir, "vendas.json")

    LOGIN_BACKGROUND_IMAGE = os.path.join(script_dir, "assets", "image.png")
    # --- FIM DO CAMINHO ---

    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow") # <<< GARANTA QUE ESTA LINHA EXISTE
        print(f"DEBUG: Caminho base do script (script_dir): {self.script_dir}") # Debug extra
        print(f"DEBUG: Caminho base do projeto (base_dir): {self.base_dir}") # Debug extra
        print(f"DEBUG: Procurando products em: {self.PRODUCTS_FILE}")
        print(f"DEBUG: Procurando vendas em: {self.SALES_FILE}")
        self.setWindowTitle("Sistema de Lanchonete Premium")
        self.setGeometry(50, 50, 1350, 900)

        # Removemos a aplicação de estilo aqui, pois será feita em login_window
        # self.setStyleSheet("")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.load_products_from_file()
        self.next_product_id = self.calculate_next_id()
        self.init_ui() # Chama login_window
    
    def clear_sales_data(self):
        """Apaga o conteúdo do arquivo de vendas (SALES_FILE) escrevendo uma lista vazia."""
        print(f"--- ATENÇÃO: Iniciando processo para zerar {self.SALES_FILE} ---")
        try:
            # Escreve uma lista JSON vazia no arquivo, sobrescrevendo o conteúdo
            with open(self.SALES_FILE, "w", encoding='utf-8') as f:
                json.dump([], f) # Escreve '[]' no arquivo
            print(f"--- SUCESSO: Arquivo {self.SALES_FILE} zerado com sucesso. ---")
            QMessageBox.information(self, "Histórico Zerado", "O histórico de vendas foi apagado com sucesso.")

            # --- Atualizar UIs Relevantes ---
            # Atualiza o Dashboard se ele existir e estiver visível
            if hasattr(self, 'dashboard_tab') and self.dashboard_tab.isVisible():
                print("-> Atualizando Dashboard após zerar vendas.")
                self.dashboard_tab.update_summary()

            # Atualiza a Aba Financeira se ela existir e estiver visível
            if hasattr(self, 'financeiro_tab') and self.financeiro_tab.isVisible():
                print("-> Atualizando FinanceiroTab após zerar vendas.")
                # Chama generate_report para limpar a tabela e mostrar total 0
                self.financeiro_tab.generate_report()

            # Adicione aqui atualizações para outras partes da UI que possam depender
            # do histórico de vendas, se houver.

        except (IOError, Exception) as e:
            print(f"--- ERRO CRÍTICO ao tentar zerar {self.SALES_FILE}: {e} ---")
            QMessageBox.critical(self, "Erro ao Zerar Histórico", f"Não foi possível apagar o histórico de vendas.\nErro: {e}")


    def calculate_next_id(self):
        if not self.products: return 1
        return max(p.get('id', 0) for p in self.products) + 1 # Mais seguro com get

    def get_next_product_id(self):
        current_id = self.next_product_id; self.next_product_id += 1; return current_id

    def load_products_from_file(self):
        if os.path.exists(self.PRODUCTS_FILE):
            try:
                with open(self.PRODUCTS_FILE, "r", encoding='utf-8') as f: self.products = json.load(f)
                default_product = {'id': 0, 'name': '', 'description': '', 'price': 0.0, 'category': 'Outros', 'image': '', 'stock': 0}
                valid_products = []
                ids_seen = set()
                for p in self.products:
                    merged_p = {**default_product, **p}
                    p_id = merged_p.get('id')
                    if isinstance(p_id, int) and p_id > 0 and p_id not in ids_seen:
                         valid_products.append(merged_p)
                         ids_seen.add(p_id)
                    else: print(f"Alerta: Produto inválido/duplicado ignorado: {p}")
                self.products = valid_products
            except (json.JSONDecodeError, IOError) as e:
                QMessageBox.warning(self, "Erro ao Carregar Produtos", f"... {e} ..."); self.products = []
        else: self.products = []
        if not self.products: # Adiciona exemplos se vazio
             self.products = [
                  {'id': 1, 'name': 'Hamburguer Clássico', 'description': 'Pão, carne, queijo', 'price': 18.50, 'category': 'Lanche', 'image': '', 'stock': 50},
                  {'id': 2, 'name': 'Coca-Cola Lata', 'description': '350ml', 'price': 5.00, 'category': 'Bebida', 'image': '', 'stock': 100},
                  {'id': 3, 'name': 'Batata Frita Média', 'description': 'Porção', 'price': 9.00, 'category': 'Lanche', 'image': '', 'stock': 80}
             ]; self.save_products_to_file()

    def save_products_to_file(self):
        try:
            with open(self.PRODUCTS_FILE, "w", encoding='utf-8') as f: json.dump(self.products, f, indent=4, ensure_ascii=False)
        except IOError as e: QMessageBox.critical(self, "Erro ao Salvar", f"... {e}")

    def init_ui(self): self.login_window()

    # --- clear_layout CORRIGIDO ---
    def clear_layout(self):
        """Remove todos os widgets e layouts aninhados do layout principal."""
        while self.main_layout.count() > 0:
            child = self.main_layout.takeAt(0)
            if child is not None:
                widget = child.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
                else:
                    layout = child.layout()
                    if layout is not None:
                        self._clear_nested_layout(layout)

    def _clear_nested_layout(self, layout):
        """Função auxiliar para limpar layouts aninhados recursivamente."""
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
                else:
                    nested_layout = item.layout()
                    if nested_layout is not None:
                        self._clear_nested_layout(nested_layout)

    # --- login_window ---
   # --- login_window (REVISADA PARA VISUAL PROFISSIONAL) ---
    # --- login_window (ADICIONANDO BACKGROUND) ---
    def login_window(self):
        print("-" * 20)
        print("DEBUG: Iniciando login_window (Debug Background)...")
        self.clear_layout()

        # --- Define o Estilo com Background ---
        base_style = "" # Não precisamos carregar style.qss se não existe

        # Prepara o caminho da imagem e verifica
        bg_image_path_qss = ""
        image_path_to_check = self.LOGIN_BACKGROUND_IMAGE # Pega o caminho CORRIGIDO
        print(f"DEBUG: Verificando existência da imagem em: {image_path_to_check}")

        if os.path.exists(image_path_to_check):
            # Converte para caminho absoluto e troca \ por / para QSS
            bg_image_path_qss = os.path.abspath(image_path_to_check).replace("\\", "/")
            print(f"DEBUG: Caminho da imagem de fundo CORRIGIDO para QSS: {bg_image_path_qss}")

            # Cria a regra QSS para o background
            # Tentativa 1: border-image (melhor para esticar)
            background_style = f"""
                QWidget#mainWindow {{
                    border-image: url('{bg_image_path_qss}') 0 0 0 0 stretch stretch;
                }}
            """
        
            # Aplica o estilo (APENAS o background se não houver base_style)
            final_login_style = base_style + background_style
            self.setStyleSheet(final_login_style)
            print("DEBUG: Estilo com imagem de fundo aplicado.")

        else:
            print(f"ERRO: Imagem de fundo NÃO encontrada em: {image_path_to_check}")
            self.setStyleSheet(base_style) # Aplica apenas o base style (vazio neste caso)
        # --- Fim da definição do estilo ---

        # --- Resto da construção da UI de login (como antes) ---
        center_widget = QWidget(); center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter); self.main_layout.addWidget(center_widget)
        login_frame = QFrame(); login_frame.setObjectName("loginFrame")
        login_frame.setFixedWidth(400); login_frame.setMaximumHeight(450)
        # login_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); border-radius: 10px;") # Frame translúcido (opcional)
        frame_layout = QVBoxLayout(login_frame)
        frame_layout.setContentsMargins(40, 40, 40, 40); frame_layout.setSpacing(25)
        self.titulo_label = QLabel("MR Lanches"); title_font = QFont(); title_font.setPointSize(24); title_font.setBold(True)
        self.titulo_label.setFont(title_font); self.titulo_label.setStyleSheet("color: #0056b3; margin-bottom: 15px; background: transparent;")
        self.titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter); frame_layout.addWidget(self.titulo_label)
        self.usuario_entry = QLineEdit(); self.usuario_entry.setPlaceholderText("Usuário"); self.usuario_entry.setMinimumHeight(40); frame_layout.addWidget(self.usuario_entry)
        self.senha_entry = QLineEdit(); self.senha_entry.setPlaceholderText("Senha"); self.senha_entry.setEchoMode(QLineEdit.EchoMode.Password); self.senha_entry.setMinimumHeight(40); frame_layout.addWidget(self.senha_entry)
        # frame_layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)) # Removido espaçador extra
        self.login_button = QPushButton("Entrar"); self.login_button.setObjectName("primaryButton"); self.login_button.setMinimumHeight(45); self.login_button.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold)); frame_layout.addWidget(self.login_button)
        self.login_button.clicked.connect(self.validar_login); self.senha_entry.returnPressed.connect(self.validar_login)
        center_layout.addWidget(login_frame); self.usuario_entry.setFocus()
        print("DEBUG: login_window com background montada (após tentativa de aplicar estilo).")
    def validar_login(self):
        usuario = self.usuario_entry.text().strip(); senha = self.senha_entry.text()
        if usuario.lower() == "caixa" and senha == "123": self.show_pos_interface()
        elif usuario.lower() == "admin" and senha == "admin": self.show_manager_interface()
        else: QMessageBox.critical(self, "Erro de Login", "Usuário ou senha inválidos!"); self.senha_entry.clear(); self.usuario_entry.setFocus(); self.usuario_entry.selectAll()

    def show_manager_interface(self):
        print("DEBUG: Chamando show_manager_interface...")
        self.clear_layout()
        self.setStyleSheet("") # Reset Estilo

        self.tab_widget = QTabWidget()
        # ... (setStyleSheet para abas) ...
        self.tab_widget.setStyleSheet("""... ESTILO DAS ABAS ...""") # Cole seu estilo aqui

        # Instancia e adiciona as abas
        self.dashboard_tab = Dashboard(self)
        self.tab_widget.addTab(self.dashboard_tab, "📊 Resumo")
        self.cadastro_tab = CadastroTab(self)
        self.tab_widget.addTab(self.cadastro_tab, "📋 Cadastros")
        self.financeiro_tab = FinanceiroTab(self)
        self.tab_widget.addTab(self.financeiro_tab, "💰 Financeiro")
        self.estoque_tab = EstoqueTab(self)
        self.tab_widget.addTab(self.estoque_tab, "📦 Estoque")
        self.vendas_tab = VendasTab(self)
        self.tab_widget.addTab(self.vendas_tab, "🛒 Vendas")
        self.fiscal_tab = FiscalTab()

        # <<< PASSA 'self' PARA ConfiguracoesTab >>>
        self.configuracoes_tab = ConfiguracoesTab(self)
        # <<< FIM DA MODIFICAÇÃO >>>

        self.tab_widget.addTab(self.fiscal_tab, "🧾 Fiscal") # Ordem ajustada
        self.tab_widget.addTab(self.configuracoes_tab, "⚙️ Configurações") # Configurações por último

        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.main_layout.addWidget(self.tab_widget)
        self.tab_changed(0)
        print("DEBUG: Interface do gerente montada.")

    def tab_changed(self, index):
        """Chamado quando o usuário troca de aba."""
        current_tab = self.tab_widget.widget(index)
        print(f"Aba alterada para: {self.tab_widget.tabText(index)}")
        # Usar hasattr para verificar se o método existe antes de chamar
        if hasattr(current_tab, 'update_summary'): current_tab.update_summary()
        elif hasattr(current_tab, 'load_data'): current_tab.load_data()
        elif hasattr(current_tab, 'load_estoque'): current_tab.load_estoque()
        elif hasattr(current_tab, 'update_products_combo'): current_tab.update_products_combo()

    def show_pos_interface(self):
        """Exibe a interface do Ponto de Venda (Caixa)."""
        print("DEBUG: Chamando show_pos_interface...") # Adicionado para log
        self.clear_layout()

        # --- INÍCIO DA MODIFICAÇÃO: Reseta o estilo da janela principal ---
        # Aplica um estilo vazio à janela principal para remover o border-image do login.
        try:
            self.setStyleSheet("") # Remove estilos inline da janela principal
            print("DEBUG: Estilo da janela principal resetado para vazio para POS.")
        except Exception as e:
            print(f"ERRO ao resetar estilo para POS: {e}")
        # --- FIM DA MODIFICAÇÃO ---

        # --- Cria o Header (código original mantido, mas com ajuste de altura) ---
        header = QLabel("Ponto de Venda - Caixa")
        # Ajustando o estilo do header ligeiramente para consistência
        header.setStyleSheet("""
            background-color: #343a40;
            color: white;
            padding: 10px 15px; /* Padding ajustado */
            font-size: 14pt;   /* Tamanho da fonte ajustado */
            font-weight: bold;
        """)
        header.setFixedHeight(45) # Altura fixa para o header
        self.main_layout.addWidget(header)
        # --- Fim do Header ---

        # --- Cria e adiciona a Interface POS ---
        # Verifica se self.products existe antes de criar a interface
        if not hasattr(self, 'products') or self.products is None:
            print("ALERTA: 'self.products' não definido ou é None ao chamar show_pos_interface. Tentando carregar...")
            self.load_products_from_file() # Tenta carregar os produtos
            if not hasattr(self, 'products') or self.products is None:
                 print("ERRO CRÍTICO: Falha ao carregar produtos para o POS.")
                 # Exibe mensagem de erro na UI
                 error_label = QLabel("Erro fatal: Não foi possível carregar os produtos para o Ponto de Venda.")
                 error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                 self.main_layout.addWidget(error_label, 1)
                 return # Interrompe a função aqui

        try:
            # Cria a instância da interface POS (código original mantido)
            self.pos_interface = POSInterface(self, self.products)

            # Adiciona a interface POS ao layout principal, fazendo-a ocupar o espaço restante
            # O segundo argumento '1' faz com que este widget se expanda verticalmente
            self.main_layout.addWidget(self.pos_interface, 1)
            print("DEBUG: Interface POS montada.")

        except Exception as e_pos:
             print(f"ERRO ao instanciar ou adicionar POSInterface: {e_pos}")
             # Exibe mensagem de erro na UI se a criação da POS falhar
             error_label = QLabel(f"Erro ao carregar o Ponto de Venda:\n{e_pos}")
             error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
             self.main_layout.addWidget(error_label, 1)
        # --- Fim da Interface POS ---

    def update_estoque_global(self, product_name, quantidade_vendida):
        updated = False
        for product in self.products:
            if product['name'] == product_name:
                product['stock'] -= quantidade_vendida
                updated = True
                if product['stock'] < 5: print(f"ALERTA: Estoque baixo para {product_name} ({product['stock']})")
                break
        if updated: self.save_products_to_file()
        if hasattr(self, 'estoque_tab') and hasattr(self, 'tab_widget') and self.tab_widget.isVisible() and self.tab_widget.currentWidget() == self.estoque_tab:
             self.estoque_tab.load_estoque()

    def registrar_venda_historico(self, total, metodo_pagamento, itens_vendidos):
        """Salva o histórico de vendas e atualiza o estoque."""
        print(f"Registrando Venda...")
        for item in itens_vendidos: self.update_estoque_global(item['produto'], item['quantidade'])
        venda = { 'data': QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate), 'itens': itens_vendidos, 'total': total, 'metodo_pagamento': metodo_pagamento }
        self.salvar_venda(venda)
        if hasattr(self, 'dashboard_tab') and hasattr(self, 'tab_widget') and self.tab_widget.isVisible() and self.tab_widget.currentWidget() == self.dashboard_tab:
            self.dashboard_tab.update_summary()
        # Atualizar relatórios só se a aba financeira estiver visível e ativa
        if hasattr(self, 'financeiro_tab') and hasattr(self, 'tab_widget') and self.tab_widget.isVisible() and self.tab_widget.currentWidget() == self.financeiro_tab:
             self.financeiro_tab.load_data()


    def salvar_venda(self, venda):
        """Salva a venda no arquivo JSON de vendas."""
        try:
            with open(self.SALES_FILE, "r", encoding='utf-8') as f: vendas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): vendas = []
        vendas.append(venda)
        try:
            with open(self.SALES_FILE, "w", encoding='utf-8') as f: json.dump(vendas, f, indent=4, ensure_ascii=False)
        except IOError as e: QMessageBox.critical(self, "Erro ao Salvar Venda", f"...: {e}")

# --- Execução ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    sistema = SistemaLanchonetePremium()
    sistema.show()
    sys.exit(app.exec())