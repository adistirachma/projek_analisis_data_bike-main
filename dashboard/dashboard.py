import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style seaborn
sns.set(style='dark')

# Menyiapkan data day_df
day_df = pd.read_csv("all_data.csv")
day_df.head()

# Menyiapkan daily_rent_df
def create_daily_rent_df(df):
    daily_rent_df = df.groupby(by='dateday').agg({
        'count': 'sum'
    }).reset_index()
    return daily_rent_df

# Menyiapkan daily_registered_rent_df
def create_daily_registered_rent_df(df):
    daily_registered_rent_df = df.groupby(by='dateday').agg({
        'registered': 'sum'
    }).reset_index()
    return daily_registered_rent_df

# Menyiapkan daily_casual_rent_df
def create_daily_casual_rent_df(df):
    daily_casual_rent_df = df.groupby(by='dateday').agg({
        'casual': 'sum'
    }).reset_index()
    return daily_casual_rent_df

# Menyiapkan workingday_rent_df
def create_workingday_rent_df(df):
    workingday_rent_df = df.groupby(by='workingday').agg({
        'count': 'sum'
    }).reset_index()
    return workingday_rent_df

# Menyiapkan holiday_rent_df
def create_holiday_rent_df(df):
    holiday_rent_df = df.groupby(by='holiday').agg({
        'count': 'sum'
    }).reset_index()
    return holiday_rent_df
   
# Menyiapkan weekday_rent_df
def create_weekday_rent_df(df):
    weekday_rent_df = df.groupby(by='weekday').agg({
        'count': 'sum'
    }).reset_index()
    return weekday_rent_df

# Menyiapkan monthly_rent_df
def create_monthly_rent_df(df):
    monthly_rent_df = df.groupby(by='month').agg({
        'count': 'sum'
    })
    ordered_months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    monthly_rent_df = monthly_rent_df.reindex(ordered_months, fill_value=0)
    return monthly_rent_df

# Menyiapkan season_rent_df
def create_season_rent_df(df):
    season_rent_df = df.groupby(by='season')[['registered', 'casual']].sum().reset_index()
    return season_rent_df


# Menyiapkan weather_rent_df
def create_weather_rent_df(df):
    weather_rent_df = df.groupby(by='weather_condition').agg({
        'count': 'sum'
    })
    return weather_rent_df

#Mengelompokkan jumlah pengguna
def demand_category(count):
    if count < 1000:
        return 'Low Demand'
    elif 1000 <= count <= 1500:
        return 'Medium Demand'
    else:
        return 'High Demand'
    
day_df['demand_group'] = day_df['count'].apply(demand_category)

#Binning untuk suhu (temp) dan kelembapan (hum)
temp_bins = [0, 0.3, 0.6, 1.0]
hum_bins = [0, 0.3, 0.6, 1.0]

temp_labels = ['Low', 'Medium', 'High']
hum_labels = ['Low', 'Medium', 'High']

day_df['temp_binned'] = pd.cut(day_df['temp'], bins=temp_bins, labels=temp_labels, include_lowest=True)
day_df['hum_binned'] = pd.cut(day_df['hum'], bins=hum_bins, labels=hum_labels, include_lowest=True)

# Membuat komponen filter
min_date = pd.to_datetime(day_df['dateday']).dt.date.min()
max_date = pd.to_datetime(day_df['dateday']).dt.date.max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = day_df[(day_df['dateday'] >= str(start_date)) & 
                (day_df['dateday'] <= str(end_date))]

# Menyiapkan berbagai dataframe
daily_rent_df = create_daily_rent_df(main_df)
daily_casual_rent_df = create_daily_casual_rent_df(main_df)
daily_registered_rent_df = create_daily_registered_rent_df(main_df)
season_rent_df = create_season_rent_df(main_df)
monthly_rent_df = create_monthly_rent_df(main_df)
weekday_rent_df = create_weekday_rent_df(main_df)
workingday_rent_df = create_workingday_rent_df(main_df)
holiday_rent_df = create_holiday_rent_df(main_df)
weather_rent_df = create_weather_rent_df(main_df)



# Membuat Dashboard secara lengkap

# Membuat judul
st.header('Bike Rental Dashboard 🚲')

# Membuat jumlah penyewaan harian
st.subheader('Daily Rentals')
col1, col2, col3 = st.columns(3)

with col1:
    daily_rent_casual = daily_casual_rent_df['casual'].sum()
    st.metric('Casual User', value= daily_rent_casual)

with col2:
    daily_rent_registered = daily_registered_rent_df['registered'].sum()
    st.metric('Registered User', value= daily_rent_registered)
 
with col3:
    daily_rent_total = daily_rent_df['count'].sum()
    st.metric('Total User', value= daily_rent_total)

#Membuat jumlah penyewaan bulanan
st.subheader('Monthly Rentals')
fig, ax = plt.subplots(figsize=(24, 8))
ax.plot(
    monthly_rent_df.index,
    monthly_rent_df['count'],
    marker='o', 
    linewidth=2,
    color='tab:blue'
)

for index, row in enumerate(monthly_rent_df['count']):
    ax.text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)

ax.tick_params(axis='x', labelsize=25, rotation=45)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)


#Membuat grafik pengguna casual vs registered on holidays
st.subheader('Casual vs. Registered Rentals on Holidays')

fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 10))

#Pengguna Casual
sns.barplot(
    x='holiday',
    y='casual',
    data=day_df,
    color='tab:pink',
    ax=axes[0]
)

axes[0].set_title('Casual Bike Rentals on Holidays')
axes[0].set_xlabel('Holiday')
axes[0].set_ylabel('Number of Casual Rentals')
axes[0].tick_params(axis='x', labelsize=15)
axes[0].tick_params(axis='y', labelsize=10)

#Pengguna Registered
sns.barplot(
    x='holiday',
    y='registered',
    data=day_df,
    color='tab:blue',
    ax=axes[1]
)

axes[1].set_title('Registered Bike Rentals on Holidays')
axes[1].set_xlabel('Holiday')
axes[1].set_ylabel('Number of Registered Rentals')
axes[1].tick_params(axis='x', labelsize=15)
axes[1].tick_params(axis='y', labelsize=10)

plt.tight_layout()
st.pyplot(fig)

# Membuat jumlah penyewaan berdasarkan season
st.subheader('Seasonly Rentals')

fig, ax = plt.subplots(figsize=(16, 8))

sns.barplot(
    data=season_rent_df,
    x='season',
    y='registered',
    label='Registered',
    color='tab:blue',
    ax=ax
)

sns.barplot(
    data=season_rent_df,
    x='season',
    y='casual',
    label='Casual',
    color='tab:pink',
    ax=ax
)

for index, row in season_rent_df.iterrows():
    ax.text(index, row['registered'], str(row['registered']), ha='center', va='bottom', fontsize=12)
    ax.text(index, row['casual'], str(row['casual']), ha='center', va='bottom', fontsize=12)

ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20, rotation=0)
ax.tick_params(axis='y', labelsize=15)
ax.legend()
st.pyplot(fig)

# Membuah jumlah penyewaan berdasarkan kondisi cuaca
st.subheader('Weatherly Rentals')

fig, ax = plt.subplots(figsize=(16, 8))

colors=["tab:blue", "tab:pink", "tab:green"]

sns.barplot(
    x=weather_rent_df.index,
    y=weather_rent_df['count'],
    palette=colors,
    ax=ax
)

for index, row in enumerate(weather_rent_df['count']):
    ax.text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)

ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)

#Membuat grafik hubungan distribusi kategori suhu dan kelembapan terhadap demand group
st.subheader('Weatherly Rentals: Impact of Weather on Bike Rentals')


fig, ax = plt.subplots(figsize=(5, 6))  


temp_grouped = day_df.groupby(['temp_binned', 'demand_group'])['count'].sum().reset_index()


sns.barplot(
    x='temp_binned',
    y='count',
    hue='demand_group',
    palette=colors,
    data=temp_grouped,
    ax=ax
)


for index, row in temp_grouped.iterrows():
    ax.text(index, row['count'] + 1, str(int(row['count'])), ha='center', va='bottom', fontsize=10)

ax.set_xlabel('Kategori Suhu (temp_binned)', fontsize=15)
ax.set_ylabel('Jumlah', fontsize=15)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
plt.title('Distribusi Kategori Suhu Terhadap Demand Group', fontsize=18)
st.pyplot(fig)


fig, ax = plt.subplots(figsize=(5, 6))


hum_grouped = day_df.groupby(['hum_binned', 'demand_group'])['count'].sum().reset_index()


sns.barplot(
    x='hum_binned',
    y='count',
    hue='demand_group',
    palette=colors,
    data=hum_grouped,
    ax=ax
)


for index, row in hum_grouped.iterrows():
    ax.text(index, row['count'] + 1, str(int(row['count'])), ha='center', va='bottom', fontsize=10)

ax.set_xlabel('Kategori Kelembapan (hum_binned)', fontsize=15)
ax.set_ylabel('Jumlah', fontsize=15)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
plt.title('Distribusi Kategori Kelembapan Terhadap Demand Group', fontsize=18)
st.pyplot(fig)


st.caption('Copyright (c) Adisti Rachma Pitaloka 2024')
