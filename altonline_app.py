class AltOnline:
    def browse_dep(self, db):
        dep_id = input("Enter the department's ID: ")      # ask the user for the department ID 
        cursor = db.cursor()
        # SQL Query
        query = f""" SELECT p.ProductID, p.Title, ROUND((p.BasePriceNet * (1 - p.DiscountPercent/100)) * (1 + p.VATPercent/100), 2) AS CurrentRetailPrice, 
		                COALESCE(ROUND(AVG(up.Stars), 2), 0 )AS AverageRating		
                    FROM PRODUCT AS p
                    LEFT JOIN USER_PRODUCT AS up
	                    ON up.ProductID = p.ProductID
                    WHERE p.DepartmentID = {dep_id}
                    GROUP BY p.ProductID
                    ORDER BY p.Title """     
        query_2 = f"SELECT DepartmentID, Title FROM DEPARTMENT WHERE ParentDepartmentID = {dep_id}"    
        cursor.execute(query_2)                 # execute query 2 in the remote database
        result = cursor.fetchall()              # get result
        if not result:                          # if the list is empty --> no children
            cursor.execute(query)               # execute query                           
            result = cursor.fetchall()              
            for x in result:                    
                print(x)        
        else:
            for x in result:
                print(x)
        cursor.close()      

    def change_disc(self, db):
        prod_id = input("Enter the product's ID: ")      # ask the user for the department ID 
        cursor = db.cursor()
        query = f"SELECT DiscountPercent FROM PRODUCT WHERE ProductID = {prod_id}"  
        cursor.execute(query)
        result = cursor.fetchall()
        print(result[0][0])
        # Discount Change
        answer = input("Do you want to change the discount? (yes/no) ")
        if answer == 'yes':
            new_discount = input("Enter the new discount percent (e.g., 10 for 10%): ")
            update_query = f"UPDATE PRODUCT SET DiscountPercent = {new_discount} WHERE ProductID = {prod_id}"   # update the discount 
            cursor.execute(update_query)
            db.commit()    # save the change in the database
        cursor.close()