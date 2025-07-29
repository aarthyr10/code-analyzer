# Comprehensive Multi-Language Codebase Analysis Report

**Generated:** 2025-07-29T19:55:35.109984
**Analyzer Version:** 3.0.0
**Analysis Type:** SonarQube-Style Multi-Language Analysis

## STEP 1: FILE EXTRACTION SUMMARY

- **Total Folders:** 27
- **Total Files Discovered:** 123
- **Total Lines of Code:** 31,546
- **Total Classes:** 16464
- **Total Methods:** 242

### Language Distribution

| Language | Files | Percentage |
|----------|-------|------------|
| Image | 18 | 14.6% |
| Java | 42 | 34.1% |
| Unknown | 20 | 16.3% |
| Html | 22 | 17.9% |
| Css | 19 | 15.4% |
| Scss | 2 | 1.6% |

## STEP 2: LANGUAGE VALIDATION

- **Validation Status:** PASSED
- **Primary Language:** JAVA
- **Supported Files:** 85

## STEP 3: SONARQUBE-STYLE ANALYSIS RESULTS

- **Files Analyzed:** 85
- **Classes Analyzed:** 35
- **Methods Analyzed:** 241
- **Lines Analyzed:** 2,030
- **Overall Quality Score:** 7.6/10
- **Average Complexity:** 1.0

### Issues Summary

| Severity | Count |
|----------|-------|
| MEDIUM | 1 |
| HIGH | 2 |

## Usage Analysis

- **Unused Classes:** 14
- **Unused Methods:** 30
- **Unused Variables:** 144
- **Potential Cleanup:** 29.79%
- **Unused Lines of Code:** 879

### All Unused Classes

| Class Name | File Path | Language | Lines of Code |
|------------|-----------|----------|---------------|
| MavenWrapperDownloader | sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | java | 107 |
| SakilaProjectApplicationTests | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/SakilaProjectApplicationTests.java | java | 24 |
| MockTests | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | java | 356 |
| SakilaProjectApplication | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/SakilaProjectApplication.java | java | 9 |
| UserDetailsServiceImpl | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/UserDetailsServiceImpl.java | java | 38 |
| FailureHandler | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/FailureHandler.java | java | 16 |
| StaffController | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/StaffController.java | java | 33 |
| CategoryService | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/CategoryService.java | java | 18 |
| FilmCategoryPK | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmCategoryPK.java | java | 37 |
| Order | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Order.java | java | 29 |
| FilmCategory | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmCategory.java | java | 49 |
| FilmActorPK | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmActorPK.java | java | 37 |
| FilmActor | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmActor.java | java | 49 |
| FilmText | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmText.java | java | 47 |

### All Unused Methods

| Class Name | Method Name | File Path | Language | Complexity |
|------------|-------------|-----------|----------|------------|
| MavenWrapperDownloader | downloadFileFromURL | sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | java | 1 |
| SakilaProjectApplicationTests | MainController1 | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/SakilaProjectApplicationTests.java | java | 1 |
| SakilaProjectApplicationTests | MainController2 | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/SakilaProjectApplicationTests.java | java | 1 |
| SakilaProjectApplicationTests | MainController3 | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/SakilaProjectApplicationTests.java | java | 1 |
| MockTests | init | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | java | 1 |
| WebSecurityConfig | configure | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/WebSecurityConfig.java | java | 1 |
| WebSecurityConfig | userDetailsService | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/WebSecurityConfig.java | java | 1 |
| WebSecurityConfig | passwordEncoder | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/WebSecurityConfig.java | java | 1 |
| WebSecurityConfig | authenticationProvider | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/WebSecurityConfig.java | java | 1 |
| WebSecurityConfig | configure | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/WebSecurityConfig.java | java | 1 |
| SuccessHandler | onAuthenticationSuccess | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/SuccessHandler.java | java | 1 |
| MvcConfig | addViewControllers | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/MvcConfig.java | java | 1 |
| UserDetailsServiceImpl | loadUserByUsername | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/UserDetailsServiceImpl.java | java | 1 |
| FailureHandler | handle | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/FailureHandler.java | java | 1 |
| StaffController | currentUser | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/StaffController.java | java | 1 |
| CustomerController | currentUser | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/CustomerController.java | java | 1 |
| CustomerController | showUsersRentalHistory | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/CustomerController.java | java | 1 |
| MainController | home | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/MainController.java | java | 1 |
| MainController | login | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/MainController.java | java | 1 |
| MainController | account | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/MainController.java | java | 1 |
| CustomerService | save | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/CustomerService.java | java | 1 |
| InventoryService | deleteInventoryItemById | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/InventoryService.java | java | 1 |
| ActorController | findActorById | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/ActorController.java | java | 1 |
| RentalService | addRental | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/RentalService.java | java | 1 |
| FilmController | rentFilm | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/FilmController.java | java | 1 |
| FilmController | showEditProductPage | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/FilmController.java | java | 1 |
| FilmController | deleteProduct | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/FilmController.java | java | 1 |
| FilmController | findFilmByID | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/FilmController.java | java | 1 |
| FilmService | save | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/FilmService.java | java | 1 |
| FilmService | deleteFilmById | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/FilmService.java | java | 1 |

### All Unused Variables

| Variable Name | Type | Scope | File Path | Line Declared |
|---------------|------|-------|-----------|---------------|
| actorRepository | ActorRepository | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| filmRepository | FilmRepository | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| customerRepository | CustomerRepository | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| categoryRepository | CategoryRepository | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| staffRepository | StaffRepository | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| rentalRepository | RentalRepository | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| inventoryRepository | InventoryRepository | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| actorService | ActorService | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| categoryService | CategoryService | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| filmService | FilmService | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| customerService | CustomerService | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| inventoryService | InventoryService | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| rentalService | RentalService | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| actorController | ActorController | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| filmController | FilmController | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| categoryController | CategoryController | class | sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 1 |
| WRAPPER_VERSION | String | class | sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 1 |
| DEFAULT_DOWNLOAD_URL | String | class | sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 1 |
| MAVEN_WRAPPER_PROPERTIES_PATH | String | class | sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 1 |
| MAVEN_WRAPPER_JAR_PATH | String | class | sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 1 |
| PROPERTY_NAME_WRAPPER_URL | String | class | sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 1 |
| --blue | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --indigo | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --purple | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --pink | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --red | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --orange | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --yellow | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --green | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --teal | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --cyan | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --white | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --gray | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --gray-dark | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --primary | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --secondary | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --success | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --info | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --warning | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --danger | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --light | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --dark | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --breakpoint-xs | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --breakpoint-sm | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --breakpoint-md | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --breakpoint-lg | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --breakpoint-xl | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --font-family-sans-serif | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --font-family-monospace | css-variable | global | sakila-master/src/main/resources/static/css/bootstrap.min.css | 6 |
| --hover | css-variable | global | sakila-master/src/main/resources/static/css/csshake.min.css | 8 |
| customerService | CustomerService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/WebSecurityConfig.java | 1 |
| staffService | StaffService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/WebSecurityConfig.java | 1 |
| successHandler | SuccessHandler | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/WebSecurityConfig.java | 1 |
| $font-Flaticon-ideas | scss-variable | global | sakila-master/src/main/resources/static/fonts/flaticon/font/_flaticon.scss | 48 |
| $font-Flaticon-flasks | scss-variable | global | sakila-master/src/main/resources/static/fonts/flaticon/font/_flaticon.scss | 49 |
| $font-Flaticon-analysis | scss-variable | global | sakila-master/src/main/resources/static/fonts/flaticon/font/_flaticon.scss | 50 |
| $font-Flaticon-ux-design | scss-variable | global | sakila-master/src/main/resources/static/fonts/flaticon/font/_flaticon.scss | 51 |
| $font-Flaticon-web-design | scss-variable | global | sakila-master/src/main/resources/static/fonts/flaticon/font/_flaticon.scss | 52 |
| $font-Flaticon-innovation | scss-variable | global | sakila-master/src/main/resources/static/fonts/flaticon/font/_flaticon.scss | 54 |
| redirectStrategy | RedirectStrategy | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/SuccessHandler.java | 1 |
| customerRepository | CustomerRepository | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/UserDetailsServiceImpl.java | 1 |
| staffRepository | StaffRepository | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/securingweb/UserDetailsServiceImpl.java | 1 |
| staffService | StaffService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/StaffController.java | 1 |
| customerService | CustomerService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/StaffController.java | 1 |
| inventoryService | InventoryService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/StaffController.java | 1 |
| filmService | FilmService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/ActorController.java | 1 |
| actorService | ActorService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/ActorController.java | 1 |
| rentalRepository | RentalRepository | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/RentalService.java | 1 |
| filmService | FilmService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/FilmController.java | 1 |
| inventoryService | InventoryService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/FilmController.java | 1 |
| rentalService | RentalService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/FilmController.java | 1 |
| customerService | CustomerService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/FilmController.java | 1 |
| filmService | FilmService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/CategoryController.java | 1 |
| categoryService | CategoryService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/CategoryController.java | 1 |
| staffRepository | StaffRepository | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/StaffService.java | 1 |
| customerService | CustomerService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/CustomerController.java | 1 |
| rentalService | RentalService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/CustomerController.java | 1 |
| inventoryService | InventoryService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/CustomerController.java | 1 |
| filmService | FilmService | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/controller/CustomerController.java | 1 |
| actorRepository | ActorRepository | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/ActorService.java | 1 |
| inventoryRepository | InventoryRepository | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/InventoryService.java | 1 |
| filmId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| title | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| description | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| releaseYear | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| rentalDuration | Integer | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| rentalRate | BigDecimal | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| length | Integer | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| replacementCost | BigDecimal | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| rating | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| specialFeatures | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| lastUpdate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Film.java | 1 |
| categoryRepository | CategoryRepository | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/CategoryService.java | 1 |
| filmId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmCategoryPK.java | 1 |
| categoryId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmCategoryPK.java | 1 |
| actorId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmActor.java | 1 |
| filmId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmActor.java | 1 |
| lastUpdate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmActor.java | 1 |
| customerRepository | CustomerRepository | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/CustomerService.java | 1 |
| filmRepository | FilmRepository | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/services/FilmService.java | 1 |
| filmId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmCategory.java | 1 |
| categoryId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmCategory.java | 1 |
| lastUpdate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmCategory.java | 1 |
| customerId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Customer.java | 1 |
| firstName | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Customer.java | 1 |
| lastName | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Customer.java | 1 |
| email | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Customer.java | 1 |
| active | byte | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Customer.java | 1 |
| createDate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Customer.java | 1 |
| lastUpdate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Customer.java | 1 |
| filmId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmText.java | 1 |
| title | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmText.java | 1 |
| description | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmText.java | 1 |
| inventoryId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Inventory.java | 1 |
| filmId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Inventory.java | 1 |
| lastUpdate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Inventory.java | 1 |
| customer | Customer | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Order.java | 1 |
| film | Film | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Order.java | 1 |
| rental | Rental | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Order.java | 1 |
| actorId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Actor.java | 1 |
| firstName | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Actor.java | 1 |
| lastName | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Actor.java | 1 |
| lastUpdate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Actor.java | 1 |
| categoryId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Category.java | 1 |
| name | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Category.java | 1 |
| lastUpdate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Category.java | 1 |
| actorId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmActorPK.java | 1 |
| filmId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/FilmActorPK.java | 1 |
| rentalId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Rental.java | 1 |
| rentalDate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Rental.java | 1 |
| inventoryId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Rental.java | 1 |
| customerId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Rental.java | 1 |
| returnDate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Rental.java | 1 |
| lastUpdate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Rental.java | 1 |
| staffId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Rental.java | 1 |
| staffId | int | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Staff.java | 1 |
| firstName | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Staff.java | 1 |
| lastName | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Staff.java | 1 |
| picture | byte | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Staff.java | 1 |
| email | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Staff.java | 1 |
| active | byte | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Staff.java | 1 |
| username | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Staff.java | 1 |
| password | String | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Staff.java | 1 |
| lastUpdate | Timestamp | class | sakila-master/src/main/java/com/sparta/engineering72/sakilaproject/entities/Staff.java | 1 |

## Coding Standards Report

- **Total Violations:** 213
- **Average Style Score:** 9.2/10
- **Files Analyzed:** 85
- **Clean Files:** 39

### Violations by Severity

| Severity | Count |
|----------|-------|
| MEDIUM | 131 |
| LOW | 81 |
| HIGH | 1 |

### Most Common Violations

| Rule | Count |
|------|-------|
| AVOID_IMPORTANT | 92 |
| CSS_BRACE_PLACEMENT | 60 |
| LINE_LENGTH | 20 |
| JAVA_METHOD_NAMING | 17 |
| INPUT_LABEL_REQUIRED | 12 |
| NO_SYSTEM_OUT | 10 |
| IMG_ALT_REQUIRED | 1 |
| TRAILING_WHITESPACE | 1 |

### Detailed Violations

| File | Line | Rule | Severity | Message | Suggestion |
|------|------|------|----------|---------|------------|
| sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/SakilaProjectApplicationTests.java | 12 | JAVA_METHOD_NAMING | MEDIUM | Method name "MainController1" should start with lowercase letter | Rename to "mainController1" |
| sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/SakilaProjectApplicationTests.java | 19 | JAVA_METHOD_NAMING | MEDIUM | Method name "MainController2" should start with lowercase letter | Rename to "mainController2" |
| sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/SakilaProjectApplicationTests.java | 26 | JAVA_METHOD_NAMING | MEDIUM | Method name "MainController3" should start with lowercase letter | Rename to "mainController3" |
| sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 292 | LINE_LENGTH | LOW | Line exceeds 120 characters (122 characters) | Break line into multiple lines |
| sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 300 | LINE_LENGTH | LOW | Line exceeds 120 characters (122 characters) | Break line into multiple lines |
| sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 332 | LINE_LENGTH | LOW | Line exceeds 120 characters (134 characters) | Break line into multiple lines |
| sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 341 | LINE_LENGTH | LOW | Line exceeds 120 characters (134 characters) | Break line into multiple lines |
| sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 85 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/src/test/java/com/sparta/engineering72/sakilaproject/MockTests.java | 363 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 50 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 52 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 66 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 77 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 82 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 86 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 89 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/.mvn/wrapper/MavenWrapperDownloader.java | 92 | NO_SYSTEM_OUT | MEDIUM | Avoid using System.out.println in production code | Use proper logging framework instead |
| sakila-master/src/main/resources/static/css/magnific-popup.css | 20 | AVOID_IMPORTANT | MEDIUM | Avoid using !important | Use more specific selectors instead |
| sakila-master/src/main/resources/static/css/magnific-popup.css | 84 | AVOID_IMPORTANT | MEDIUM | Avoid using !important | Use more specific selectors instead |
| sakila-master/src/main/resources/static/css/magic.min.css | 5 | CSS_BRACE_PLACEMENT | LOW | Opening brace should be at end of line | Move opening brace to end of selector line |

## Variable Analysis

- **Total Variables:** 355
- **Unused Variables:** 144

### Variables by Type

| Type | Count |
|------|-------|
| html-id | 8 |
| html-class | 201 |
| ActorRepository | 2 |
| FilmRepository | 2 |
| CustomerRepository | 3 |
| CategoryRepository | 2 |
| StaffRepository | 3 |
| RentalRepository | 2 |
| InventoryRepository | 2 |
| ActorService | 2 |
| CategoryService | 2 |
| FilmService | 5 |
| CustomerService | 5 |
| InventoryService | 4 |
| RentalService | 3 |
| ActorController | 1 |
| FilmController | 1 |
| CategoryController | 1 |
| String | 22 |
| css-variable | 30 |
| StaffService | 2 |
| SuccessHandler | 1 |
| scss-variable | 7 |
| RedirectStrategy | 1 |
| int | 21 |
| Integer | 2 |
| BigDecimal | 2 |
| Timestamp | 12 |
| byte | 3 |
| Customer | 1 |
| Film | 1 |
| Rental | 1 |

### Variables by Scope

| Scope | Count |
|-------|-------|
| global | 246 |
| class | 109 |

## Complexity Analysis

### Complexity by Language

| Language | Average Complexity | Class Count |
|----------|-------------------|-------------|
| Java | 1.0 | 35 |

### Most Complex Classes

| Class Name | Language | Complexity Score |
|------------|----------|------------------|
| MavenWrapperDownloader | java | 1.00 |
| SakilaProjectApplicationTests | java | 1.00 |
| MockTests | java | 1.00 |
| SakilaProjectApplication | java | 1.00 |
| WebSecurityConfig | java | 1.00 |
| SuccessHandler | java | 1.00 |
| MvcConfig | java | 1.00 |
| UserDetailsServiceImpl | java | 1.00 |
| FailureHandler | java | 1.00 |
| StaffController | java | 1.00 |

### Most Complex Methods

| Class | Method | Complexity |
|-------|--------|-----------|
| MavenWrapperDownloader | main | 1 |
| MavenWrapperDownloader | downloadFileFromURL | 1 |
| SakilaProjectApplicationTests | MainController1 | 1 |
| SakilaProjectApplicationTests | MainController2 | 1 |
| SakilaProjectApplicationTests | MainController3 | 1 |
| MockTests | init | 1 |
| MockTests | testActorById | 1 |
| MockTests | testActorByFirstName | 1 |
| MockTests | testActorByLastName | 1 |
| MockTests | testActorByMore | 1 |
| MockTests | testActorByFullName | 1 |
| MockTests | testFilmByID | 1 |
| MockTests | testFilmByDescritption | 1 |
| MockTests | testFilmByRating | 1 |
| MockTests | testFilmByLength | 1 |
| MockTests | testFilmByName | 1 |
| MockTests | testFilmByDescription | 1 |
| MockTests | testFilms | 1 |
| MockTests | testCategoryById | 1 |
| MockTests | testCategoryByName | 1 |

## Improvement Suggestions

### Code Cleanup (MEDIUM)
Found 14 unused classes that can be removed

**Action:** Remove unused classes to reduce codebase size and complexity

**Affected Items:**
- MavenWrapperDownloader (java)
- SakilaProjectApplicationTests (java)
- MockTests (java)
- SakilaProjectApplication (java)
- UserDetailsServiceImpl (java)
- FailureHandler (java)
- StaffController (java)
- CategoryService (java)
- FilmCategoryPK (java)
- Order (java)

**Potential LOC Reduction:** 849 lines

### Code Cleanup (LOW)
Found 30 unused methods that can be removed

**Action:** Remove unused methods to improve code maintainability

**Affected Items:**
- MavenWrapperDownloader.downloadFileFromURL (java)
- SakilaProjectApplicationTests.MainController1 (java)
- SakilaProjectApplicationTests.MainController2 (java)
- SakilaProjectApplicationTests.MainController3 (java)
- MockTests.init (java)
- WebSecurityConfig.configure (java)
- WebSecurityConfig.userDetailsService (java)
- WebSecurityConfig.passwordEncoder (java)
- WebSecurityConfig.authenticationProvider (java)
- WebSecurityConfig.configure (java)

**Potential LOC Reduction:** 30 lines

## Analysis Metrics

- **Analysis Duration:** 0.42 seconds
- **Files Processed:** 123
- **Classes Analyzed:** 35
- **Methods Analyzed:** 0
- **Variables Analyzed:** 355
- **Issues Found:** 3
- **Style Violations:** 213
