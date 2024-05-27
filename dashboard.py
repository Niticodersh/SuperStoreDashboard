import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import tempfile

# Set Streamlit page configuration
st.set_page_config(page_title="SuperStore Analysis", page_icon=":bar_chart:", layout="wide")

# Page title
st.title(":bar_chart: SuperStore Dashboard")

st.markdown('''
    <style>
    div.block-container {
        padding-top: 3rem;
    }
    </style>
''', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))
df = pd.DataFrame()
if fl is not None:
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(fl.getvalue())
        temp_file_path = tmp_file.name

    filename = fl.name
    st.write(f"Uploaded file: {filename}")
    # Initialize the DataFrame
    # Read the file into a DataFrame based on the file type
    if filename.endswith('.csv') or filename.endswith('.txt'):
        df = pd.read_csv(temp_file_path)
    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        df = pd.read_excel(temp_file_path)

    # Display the DataFrame
    # st.write(df)

    col1, col2 = st.columns((2))
    df["Order Date"] = pd.to_datetime(df["Order Date"])

    startDate = pd.to_datetime(df["Order Date"]).min()
    endDate = pd.to_datetime(df["Order Date"]).max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))

    with col2:
        date2 = pd.to_datetime((st.date_input("End Date", endDate)))

    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()
    # st.write(df)

    st.sidebar.header("Choose your filter")
    region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
    if not region:
        df2 = df.copy()
    else:
        df2 = df[df["Region"].isin(region)]

    state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
    if not state:
        df3 = df2.copy()
    else:
        df3 = df2[df2["State"].isin(state)]

    city = st.sidebar.multiselect("Pick the City", df3["City"].unique())
    if not city:
        df4 = df3.copy()
    else:
        df4 = df3[df3["City"].isin(city)]

    if not region and not state and not city:
        filtered_df = df
    elif not state and not city:
        # filtered_df = df[df["Region"].isin(region)]
        filtered_df = df2
    elif not region and not city:
        filtered_df = df[df["State"].isin(state)]
    elif not region and not state:
        filtered_df = df[df["City"].isin(city)]
    elif city and state:
        filtered_df = df3[df["State"].isin(state) & df["City"].isin(city)]
    elif region and state:
        # filtered_df = df3[df["State"].isin(region) & df["State"].isin(state)]
        filtered_df = df3
    elif region and city:
        # filtered_df = df3[df["State"].isin(region) & df["City"].isin(city)]
        filtered_df = df2[df["City"].isin(city)]
    # elif city:
    #     filtered_df = df3[df3["city"].isin(city)]
    else:
        # filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["city"].isin(city)]
        filtered_df = df4

    # st.write(filtered_df)

    category_df = filtered_df.groupby(by=["Category"], as_index= False)["Sales"].sum()
    # st.write(category_df)
    with col1:
        st.subheader("Category wise Sales")
        fig = px.bar(category_df, x="Category", y="Sales", text=[f'{x:.2f}' for x in category_df["Sales"]], template="seaborn")
        st.plotly_chart(fig, use_container_width=True, height=200)

    with col2:
        st.subheader("Region wise Sales")
        fig = px.pie(filtered_df, values='Sales', names="Region", hole=0.5)
        fig.update_traces(text = filtered_df["Region"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 = st.columns((2))
    with cl1:
        with st.expander("Category_ViewData"):
            st.write(category_df.style.background_gradient(cmap="Blues"))
            csv = category_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv", help="'click here to download daata as csv file")

    with cl2:
        with st.expander("Region_ViewData"):
            region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
            st.write(region.style.background_gradient(cmap="Oranges"))
            csv = region.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv", help="'click here to download daata as csv file")

    filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
    st.subheader('Time Series Analysis')

    linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime('%Y : %b'))["Sales"].sum()).reset_index()
    fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales":"Amount"}, height=500, width=1000, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("View Data of Time Series"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))
        csv = linechart.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv", help="click here to download data as csv file")


    st.subheader("Hierarchical view of Sales using TreeMap")
    fig3 = px.treemap(filtered_df, path=["Region","Category","Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")
    fig3.update_layout(width=800, height=650)
    st.plotly_chart(fig3, use_container_width=True)

    chart1, chart2 = st.columns((2))
    with chart1:
        st.subheader('Segment wise Sales')
        fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
        fig.update_traces(text=filtered_df["Segment"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        st.subheader('Category wise Sales')
        fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
        fig.update_traces(text=filtered_df["Category"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    import plotly.figure_factory as ff
    st.subheader(":point_right: Month wise Sub-Category Sales Summary")
    with st.expander("Summary Table"):
        df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
        fig = ff.create_table(df_sample, colorscale="Cividis")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("Month wise sub-Category Table")
        filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
        sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
        st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

    data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
    data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot", titlefont=dict(size=20),
                           xaxis=dict(title="Sales", titlefont=dict(size=19)), yaxis=dict(title="Profit", titlefont=dict(size=19)))
    st.plotly_chart(data1, use_container_width=True)

    with st.expander("View Data"):
        st.write(filtered_df.style.background_gradient(cmap="Oranges"))

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")