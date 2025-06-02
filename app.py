import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

# Configuração da página
st.set_page_config(
    page_title="Cadastro de Pessoas Físicas",
    page_icon="👥",
    layout="wide"
)

# Nome do arquivo Excel
EXCEL_FILE = "cadastro_pessoas.xlsx"

def criar_arquivo_excel():
    """Cria o arquivo Excel se não existir"""
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=[
            'ID', 'Nome Completo', 'CPF', 'RG', 'Data Nascimento',
            'Email', 'Telefone', 'CEP', 'Endereço', 'Cidade',
            'Estado', 'Profissão', 'Data Cadastro'
        ])
        df.to_excel(EXCEL_FILE, index=False)

def carregar_dados():
    """Carrega dados do Excel"""
    try:
        return pd.read_excel(EXCEL_FILE)
    except:
        criar_arquivo_excel()
        return pd.read_excel(EXCEL_FILE)

def salvar_dados(df):
    """Salva dados no Excel"""
    df.to_excel(EXCEL_FILE, index=False)

def validar_cpf(cpf):
    """Validação básica de CPF"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()

def validar_email(email):
    """Validação básica de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def main():
    st.title("📋 Sistema de Cadastro de Pessoas Físicas")
    st.markdown("---")
    
    # Sidebar para navegação
    st.sidebar.title("📁 Menu")
    opcao = st.sidebar.selectbox(
        "Escolha uma opção:",
        ["Novo Cadastro", "Consultar Cadastros", "Editar Cadastro", "Estatísticas"]
    )
    
    # Carrega dados existentes
    df = carregar_dados()
    
    if opcao == "Novo Cadastro":
        st.header("➕ Novo Cadastro")
        
        with st.form("form_cadastro"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo *", placeholder="João da Silva")
                cpf = st.text_input("CPF *", placeholder="000.000.000-00")
                rg = st.text_input("RG", placeholder="12.345.678-9")
                data_nasc = st.date_input("Data de Nascimento")
                email = st.text_input("Email *", placeholder="joao@email.com")
                telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")
            
            with col2:
                cep = st.text_input("CEP", placeholder="00000-000")
                endereco = st.text_input("Endereço", placeholder="Rua das Flores, 123")
                cidade = st.text_input("Cidade", placeholder="São Paulo")
                estado = st.selectbox("Estado", [
                    "", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
                    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
                ])
                profissao = st.text_input("Profissão", placeholder="Engenheiro")
            
            submit = st.form_submit_button("💾 Cadastrar")
            
            if submit:
                # Validações
                erros = []
                
                if not nome.strip():
                    erros.append("Nome é obrigatório")
                
                if not cpf.strip():
                    erros.append("CPF é obrigatório")
                elif not validar_cpf(cpf):
                    erros.append("CPF inválido")
                elif not df.empty and cpf in df['CPF'].values:
                    erros.append("CPF já cadastrado")
                
                if not email.strip():
                    erros.append("Email é obrigatório")
                elif not validar_email(email):
                    erros.append("Email inválido")
                elif not df.empty and email in df['Email'].values:
                    erros.append("Email já cadastrado")
                
                if erros:
                    for erro in erros:
                        st.error(erro)
                else:
                    # Gerar novo ID
                    novo_id = len(df) + 1 if not df.empty else 1
                    
                    # Criar novo registro
                    novo_registro = {
                        'ID': novo_id,
                        'Nome Completo': nome,
                        'CPF': cpf,
                        'RG': rg,
                        'Data Nascimento': data_nasc.strftime('%d/%m/%Y'),
                        'Email': email,
                        'Telefone': telefone,
                        'CEP': cep,
                        'Endereço': endereco,
                        'Cidade': cidade,
                        'Estado': estado,
                        'Profissão': profissao,
                        'Data Cadastro': datetime.now().strftime('%d/%m/%Y %H:%M')
                    }
                    
                    # Adicionar ao DataFrame
                    df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                    
                    # Salvar no Excel
                    salvar_dados(df)
                    
                    st.success("✅ Cadastro realizado com sucesso!")
                    st.balloons()
    
    elif opcao == "Consultar Cadastros":
        st.header("🔍 Consultar Cadastros")
        
        if df.empty:
            st.info("Nenhum cadastro encontrado.")
        else:
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filtro_nome = st.text_input("Filtrar por Nome")
            with col2:
                filtro_cidade = st.text_input("Filtrar por Cidade")
            with col3:
                filtro_estado = st.selectbox("Filtrar por Estado", [""] + list(df['Estado'].dropna().unique()))
            
            # Aplicar filtros
            df_filtrado = df.copy()
            
            if filtro_nome:
                df_filtrado = df_filtrado[df_filtrado['Nome Completo'].str.contains(filtro_nome, case=False, na=False)]
            
            if filtro_cidade:
                df_filtrado = df_filtrado[df_filtrado['Cidade'].str.contains(filtro_cidade, case=False, na=False)]
            
            if filtro_estado:
                df_filtrado = df_filtrado[df_filtrado['Estado'] == filtro_estado]
            
            # Exibir resultados
            st.write(f"**{len(df_filtrado)} cadastro(s) encontrado(s)**")
            
            if not df_filtrado.empty:
                # Configurar colunas para exibição
                colunas_exibir = ['ID', 'Nome Completo', 'CPF', 'Email', 'Telefone', 'Cidade', 'Estado']
                st.dataframe(
                    df_filtrado[colunas_exibir],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Opção para download
                st.download_button(
                    label="📥 Download Excel",
                    data=df_filtrado.to_excel(index=False).encode(),
                    file_name=f"cadastros_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    elif opcao == "Editar Cadastro":
        st.header("✏️ Editar Cadastro")
        
        if df.empty:
            st.info("Nenhum cadastro encontrado.")
        else:
            # Seleção do cadastro
            opcoes_cadastro = [f"{row['ID']} - {row['Nome Completo']}" for _, row in df.iterrows()]
            cadastro_selecionado = st.selectbox("Selecione o cadastro para editar:", [""] + opcoes_cadastro)
            
            if cadastro_selecionado:
                id_selecionado = int(cadastro_selecionado.split(" - ")[0])
                registro = df[df['ID'] == id_selecionado].iloc[0]
                
                with st.form("form_edicao"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nome = st.text_input("Nome Completo", value=registro['Nome Completo'])
                        cpf = st.text_input("CPF", value=registro['CPF'])
                        rg = st.text_input("RG", value=str(registro['RG']) if pd.notna(registro['RG']) else "")
                        email = st.text_input("Email", value=registro['Email'])
                        telefone = st.text_input("Telefone", value=str(registro['Telefone']) if pd.notna(registro['Telefone']) else "")
                    
                    with col2:
                        cep = st.text_input("CEP", value=str(registro['CEP']) if pd.notna(registro['CEP']) else "")
                        endereco = st.text_input("Endereço", value=str(registro['Endereço']) if pd.notna(registro['Endereço']) else "")
                        cidade = st.text_input("Cidade", value=str(registro['Cidade']) if pd.notna(registro['Cidade']) else "")
                        estado = st.selectbox("Estado", [
                            "", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                            "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
                            "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
                        ], index=0 if pd.isna(registro['Estado']) else [
                            "", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                            "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
                            "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
                        ].index(registro['Estado']))
                        profissao = st.text_input("Profissão", value=str(registro['Profissão']) if pd.notna(registro['Profissão']) else "")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        atualizar = st.form_submit_button("💾 Atualizar")
                    with col_btn2:
                        excluir = st.form_submit_button("🗑️ Excluir", type="secondary")
                    
                    if atualizar:
                        # Validações
                        erros = []
                        
                        if not nome.strip():
                            erros.append("Nome é obrigatório")
                        
                        if not cpf.strip():
                            erros.append("CPF é obrigatório")
                        elif not validar_cpf(cpf):
                            erros.append("CPF inválido")
                        
                        if not email.strip():
                            erros.append("Email é obrigatório")
                        elif not validar_email(email):
                            erros.append("Email inválido")
                        
                        if erros:
                            for erro in erros:
                                st.error(erro)
                        else:
                            # Atualizar registro
                            df.loc[df['ID'] == id_selecionado, 'Nome Completo'] = nome
                            df.loc[df['ID'] == id_selecionado, 'CPF'] = cpf
                            df.loc[df['ID'] == id_selecionado, 'RG'] = rg
                            df.loc[df['ID'] == id_selecionado, 'Email'] = email
                            df.loc[df['ID'] == id_selecionado, 'Telefone'] = telefone
                            df.loc[df['ID'] == id_selecionado, 'CEP'] = cep
                            df.loc[df['ID'] == id_selecionado, 'Endereço'] = endereco
                            df.loc[df['ID'] == id_selecionado, 'Cidade'] = cidade
                            df.loc[df['ID'] == id_selecionado, 'Estado'] = estado
                            df.loc[df['ID'] == id_selecionado, 'Profissão'] = profissao
                            
                            salvar_dados(df)
                            st.success("✅ Cadastro atualizado com sucesso!")
                            st.rerun()
                    
                    if excluir:
                        if st.session_state.get('confirmar_exclusao', False):
                            df = df[df['ID'] != id_selecionado]
                            salvar_dados(df)
                            st.success("✅ Cadastro excluído com sucesso!")
                            st.session_state.confirmar_exclusao = False
                            st.rerun()
                        else:
                            st.session_state.confirmar_exclusao = True
                            st.warning("⚠️ Clique novamente para confirmar a exclusão!")
    
    else:  # Estatísticas
        st.header("📊 Estatísticas")
        
        if df.empty:
            st.info("Nenhum cadastro encontrado.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Cadastros", len(df))
            
            with col2:
                cadastros_hoje = len(df[df['Data Cadastro'].str.contains(datetime.now().strftime('%d/%m/%Y'), na=False)])
                st.metric("Cadastros Hoje", cadastros_hoje)
            
            with col3:
                estados_unicos = df['Estado'].dropna().nunique()
                st.metric("Estados Representados", estados_unicos)
            
            with col4:
                cidades_unicas = df['Cidade'].dropna().nunique()
                st.metric("Cidades Diferentes", cidades_unicas)
            
            # Gráficos
            st.subheader("📈 Distribuição por Estado")
            if not df['Estado'].dropna().empty:
                estado_counts = df['Estado'].value_counts()
                st.bar_chart(estado_counts)
            
            st.subheader("🏙️ Top 10 Cidades")
            if not df['Cidade'].dropna().empty:
                cidade_counts = df['Cidade'].value_counts().head(10)
                st.bar_chart(cidade_counts)

if __name__ == "__main__":
    main()
