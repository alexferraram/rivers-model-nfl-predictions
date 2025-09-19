# PFF Data Export Instructions

## 🎯 **Goal**
Export real PFF team grades data from [https://premium.pff.com/nfl/teams/2025/REGPO](https://premium.pff.com/nfl/teams/2025/REGPO) to improve the RIVERS model's PFF matchup score calculations.

## 📋 **Step-by-Step Process**

### **Step 1: Access PFF Premium**
1. Go to [https://premium.pff.com/login](https://premium.pff.com/login)
2. Log in with your credentials
3. Navigate to [https://premium.pff.com/nfl/teams/2025/REGPO](https://premium.pff.com/nfl/teams/2025/REGPO)

### **Step 2: Export the Data**
You have two options:

#### **Option A: CSV Export (Recommended)**
1. **Select all data** from the table (Ctrl+A or Cmd+A)
2. **Copy the data** (Ctrl+C or Cmd+C)
3. **Open Excel or Google Sheets**
4. **Paste the data** (Ctrl+V or Cmd+V)
5. **Save as CSV** with the filename `pff_exported_data.csv`
6. **Place the file** in the `/Users/alexferraramorales/NFL/` directory

#### **Option B: JSON Export**
1. **Manually copy** the data for each team
2. **Use the template** in `pff_data_template.json` as a guide
3. **Replace the values** with actual PFF grades
4. **Save as** `pff_exported_data.json`
5. **Place the file** in the `/Users/alexferraramorales/NFL/` directory

### **Step 3: Data Format**
The data should include these columns/grades for each team:
- **Team Name** (e.g., "Buffalo Bills")
- **Overall Grade**
- **Offense Overall Grade**
- **Passing Grade**
- **Pass Blocking Grade**
- **Receiving Grade**
- **Rushing Grade**
- **Run Blocking Grade**
- **Defense Overall Grade**
- **Run Defense Grade**
- **Tackling Grade**
- **Pass Rush Grade**
- **Coverage Grade**
- **Special Teams Grade**

### **Step 4: Verify the Data**
After exporting, the model will automatically:
1. **Detect** the exported file
2. **Parse** the data
3. **Validate** the grades
4. **Convert** to the required format
5. **Use** for PFF matchup calculations

## 🔧 **Files Created**
- `pff_data_template.csv` - CSV template with all 32 teams
- `pff_data_template.json` - JSON template with all 32 teams
- `pff_data_parser.py` - Parser to read your exported data
- `pff_data_system.py` - Updated to use exported data

## ✅ **Testing**
Once you've exported the data, run:
```bash
cd /Users/alexferraramorales/NFL
python3 pff_data_parser.py
```

This will test the parser with your exported data.

## 🎯 **Expected Result**
After exporting the real PFF data, the model will:
- Use **actual PFF grades** instead of default 70.0 values
- Calculate **accurate PFF matchup scores** for all teams
- Provide **more precise predictions** for Week 3 and beyond

## 📞 **Need Help?**
If you encounter any issues:
1. Check that the file is saved in the correct directory
2. Verify the data format matches the template
3. Run the parser test to check for errors
4. The model will fall back to realistic data if parsing fails

---

**Note**: The current system is working with realistic fallback data, but getting the actual PFF data will significantly improve prediction accuracy!

