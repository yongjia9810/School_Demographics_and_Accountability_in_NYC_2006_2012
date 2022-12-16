import streamlit as st
import plotly.express as px
import pandas as pd


st.set_page_config(layout="wide")

Header = st.title('School Demographics and Accountability in NYC (2006-2012)')


rawData = pd.read_csv('data.csv')

#Wrangle data
clearData = rawData
clearData["Name"] = rawData["Name"].str.rstrip()



columnList = list(clearData.columns)
i = 2
while i < len(columnList):
    clearData[columnList[i]] = pd.to_numeric(clearData[columnList[i]], errors='coerce')
    i+=1

clearData["District"] = clearData["DBN"].str[:3]
clearData["Number"] = clearData["DBN"].str[3:6]
clearData["Borough"] = clearData["DBN"].str[2]
clearData["Borough"] = clearData["Borough"].replace(['M', 'X', 'K', 'Q', 'R'], ['Manhattan', 'Bronx', "Brooklyn", "Queens", "Staten Island"])

clearData["schoolyear"] = clearData["schoolyear"].astype(str)
clearData["schoolyear"] = clearData["schoolyear"].str[:4]+"-"+clearData["schoolyear"].str[4:8]
clearData=clearData.rename(columns={
    'total_enrollment':'Total Enrollment',
    "schoolyear": "School Year",
    "asian_num": "Asian Number",
    "asian_per": "Asian Percentage",
    "black_num": "Black Number",
    "black_per": "Black Percentage",
    "hispanic_num": "Hispanic Number",
    "hispanic_per": "Hispanic Percentage",
    "white_num": "White Number",
    "white_per": "White Percentage",
    "male_num": "Male Number",
    "male_per": "Male Percentage",
    "female_num": "Female Number",
    "female_per": "Female Percentage",
    "ell_num": "English Languages Learners Number",
    "ell_percent": "English Languages Learners Percentage",
    "sped_num": "Special Education Number",
    "sped_percent": "Special Education Percentage",
    "ctt_num": "Collarborative Team Teaching Number",
    "selfcontained_num": "Self Contained Number",
    "fl_percent": "Free Lunch Percentage",
    "frl_percent": "Free and Reduced Lunch Percentage",
})



clearData['Free Lunch/Free and Reduced Lunch Percentage'] = clearData[clearData.columns[3:5]].apply(
    lambda x: ','.join(x.dropna().astype(str)),
    axis=1
)
clearData['Free Lunch/Free and Reduced Lunch Percentage'] = pd.to_numeric(clearData['Free Lunch/Free and Reduced Lunch Percentage'], errors='coerce')

st.dataframe(clearData)

#Total Enrollment
# st.write("Total Enrollment")
totalEnrollment = clearData.groupby('School Year', as_index =False).sum()

# st.dataframe(totalEnrollment)

col1, col2 = st.columns(2)

with col1:
    fig = px.line(totalEnrollment, x="School Year", y='Total Enrollment', markers=True)
    fig.update_layout(title='Total Enrollment between 2006 to 2012:',
                      )
    st.plotly_chart(fig)

with col2:
   gradeEnrollment = pd.melt(totalEnrollment, id_vars='School Year', value_vars=["prek","k","grade1","grade2","grade3","grade4","grade5",
     "grade6","grade7","grade8","grade9","grade10","grade11","grade12"],
             var_name='Grade', value_name='Total Enrollment')
   # st.dataframe(gradeEnrollment)
   fig = px.line(gradeEnrollment, x='School Year', y='Total Enrollment', color='Grade', markers=True)
   fig.update_layout(title='Total Enrollment in each grade of all schools:',
                              )
   st.plotly_chart(fig)




#choose year

yearSelect = st.sidebar.selectbox(
    'Choose year you want to know:',
    ("2005-2006","2006-2007","2007-2008","2008-2009","2009-2010","2010-2011","2011-2012"))

yearData = clearData.query("`School Year`== @yearSelect")
st.subheader("You selected: ")
st.write("School Year", yearSelect)


#Adjust the range of total enrollment
st.sidebar.markdown("---")
enrollmentSelect = st.sidebar.slider("Adjust total enrollment:",
                                     min_value=int(yearData["Total Enrollment"].min()),
                                     max_value=int(yearData["Total Enrollment"].max()),
                                     value=(int(yearData["Total Enrollment"].min()), int(yearData["Total Enrollment"].max())),
                                     step=1)



mask = yearData["Total Enrollment"].between(enrollmentSelect[0], enrollmentSelect[1])
totalRangeData = yearData[mask]

#Filter borough
st.sidebar.markdown("---")

container1 = st.sidebar.container()
all1 = st.sidebar.checkbox("Select all boroughs")


if all1:
    boroughSelect = container1.multiselect(
        'Choose boroughs you want to look up:',
        options=totalRangeData["Borough"].unique(),
        default=totalRangeData["Borough"].unique()
    )
else:
    boroughSelect = container1.multiselect(
        'Choose boroughs you want to look up:',
        options=totalRangeData["Borough"].unique(),
        default=[]
    )

if not boroughSelect:
    st.sidebar.error("There is no values")
    st.stop()

else:
    boroughData = totalRangeData.query("Borough == @boroughSelect")

    # st.dataframe(boroughData)




#Filter name in selected borough

st.sidebar.markdown("---")

container2 = st.sidebar.container()
all2 = st.sidebar.checkbox("Select all districts")


if all2:
    districtSelect = container2.multiselect(
        'Choose districts you want to look up:',
        options=boroughData["District"].unique(),
        default=boroughData["District"].unique()
    )
else:
    districtSelect = container2.multiselect(
        'Choose districts you want to look up:',
        options=boroughData["District"].unique(),
        default=[]
    )

if not districtSelect:
    st.sidebar.error("There is no values")
    st.stop()

else:
    districtData = boroughData.query("District == @districtSelect")

    # st.dataframe(districtData)




    #Total enrollments of each grade in this year

    st.sidebar.markdown("---")

    container3 = st.sidebar.container()
    all3 = st.sidebar.checkbox("Select all schools")


    if all3:
        schoolSelect = container3.multiselect(
            'Choose schools you want to look up:',
            options=sorted(districtData["Name"].unique()),
            default=sorted(districtData["Name"].unique())
        )
    else:
        schoolSelect = container3.multiselect(
            'Choose schools you want to look up:',
            options=sorted(districtData["Name"].unique()),
            default=[]
        )

    if not schoolSelect:
        st.sidebar.error("There is no values")
        st.stop()

    else:
        schoolNameData = districtData.query("Name == @schoolSelect")
        # st.dataframe(schoolNameData)

        schoolNameDataSum = pd.melt(schoolNameData, id_vars=['Borough', "Name"],
                                    value_vars=["prek","k","grade1","grade2","grade3","grade4","grade5",
                                                "grade6","grade7","grade8","grade9","grade10","grade11","grade12"],
                                    var_name='Grade',
                                    value_name='Total Enrollment',)
        # st.dataframe(schoolNameDataSum)

        # schoolNameDataSum = schoolNameDataSum.groupby('Grade', as_index=False).sum()




        fig = px.bar(schoolNameDataSum, x='Grade', y='Total Enrollment',hover_data=['Name'], color="Borough")
        # Edit the layout
        fig.update_layout(title='Total Enrollment in each grade of selected schools in this school year:',
                          )

        st.plotly_chart(fig)

        #Race percentagedistrict
        schoolNameDataRace = pd.melt(schoolNameData, id_vars=['District', "Name"],
                                    value_vars=["Asian Number",
                                                "Black Number",
                                                "Hispanic Number",
                                                "White Number", ],
                                    var_name='Race', value_name='Number')

        schoolNameDataRace = schoolNameDataRace.groupby('Race', as_index=False).sum()

        fig = px.pie(schoolNameDataRace, values='Number', names='Race', title='Number of each race:')


        st.plotly_chart(fig)

        # Gender percentage
        schoolNameDataGender = pd.melt(schoolNameData, id_vars=['District', "Name"],
                                     value_vars=["Male Number",
                                                 "Female Number",
                                                 ],
                                     var_name='Gender', value_name='Number')

        schoolNameDataGender = schoolNameDataGender.groupby('Gender', as_index=False).sum()

        # st.dataframe(schoolNameDataGender)
        fig = px.pie(schoolNameDataGender, values='Number', names='Gender', title='Number of Males and Females')

        st.plotly_chart(fig)

        schoolNameDataStats = pd.melt(schoolNameData, id_vars=['Borough', "Name"],
                                      value_vars=["English Languages Learners Number",
                                                  "Special Education Number",
                                                  "Collarborative Team Teaching Number",
                                                  "Self Contained Number",
                                                ],
                                      var_name='Stats',
                                      value_name='Number', )
        # st.dataframe(schoolNameDataStats)

        fig = px.bar(schoolNameDataStats, x='Stats', y='Number', hover_data=['Name'], color="Borough")
        fig.update_layout(title='Total Enrollment(Other kinds of education) in each grade of selected schools in this school year:',
                          )



        st.plotly_chart(fig)

        #Scatter plot

        schoolNameDataRacePer= pd.melt(schoolNameData, id_vars=["Borough", 'District', "Name","Free Lunch/Free and Reduced Lunch Percentage"],
                                     value_vars=["Asian Percentage",
                                                 "Black Percentage",
                                                 "Hispanic Percentage",
                                                 "White Percentage", ],
                                     var_name='Race', value_name='Race Percentage')
        # st.dataframe(schoolNameDataRacePer)


        fig = px.scatter(schoolNameDataRacePer, x="Race Percentage", y="Free Lunch/Free and Reduced Lunch Percentage",
                         color="Race",
                         symbol="Race",
                         hover_data=['Name', "Borough", "District"])
        fig.update_yaxes(  # the y-axis is in dollars
            ticksuffix="%", showgrid=True
        )
        fig.update_xaxes(  # the x-axis is in dollars
            ticksuffix="%", showgrid=True
        )
        fig.update_layout(title='Free Lunch/Free and Reduced Lunch Percentage × Each Race Percentage',
                          )
        st.plotly_chart(fig)